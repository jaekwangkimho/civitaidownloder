import requests
import os
from tqdm import tqdm
from flask import Flask, render_template, request

app = Flask(__name__)

def fetch_models(query_params):
    url = "https://civitai.com/api/v1/models"

    response = requests.get(url, params=query_params)

    if response.status_code == 200:
        data = response.json()
        models = data["items"]
        metadata = data.get("metadata", {})
        total_pages = metadata.get("totalPages", 0)
        current_page = metadata.get("currentPage", 0)

        if total_pages > 1:
            for page in range(current_page + 1, total_pages + 1):
                query_params["page"] = page
                response = requests.get(url, params=query_params)

                if response.status_code == 200:
                    data = response.json()
                    models.extend(data["items"])
                else:
                    print(f"API 요청에 실패했습니다. 응답 코드: {response.status_code}")
                    break

        if "nextPage" in metadata:
            next_page = metadata["nextPage"]
            while next_page:
                response = requests.get(next_page)

                if response.status_code == 200:
                    data = response.json()
                    models.extend(data["items"])
                    metadata = data.get("metadata", {})
                    next_page = metadata.get("nextPage")
                else:
                    print(f"API 요청에 실패했습니다. 응답 코드: {response.status_code}")
                    break

        return models
    else:
        print(f"API 요청에 실패했습니다. 응답 코드: {response.status_code}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        limit = int(request.form['limit'])
        page = int(request.form['page'])
        types = request.form['types']
        tag = request.form['tag'] if 'tag' in request.form else None
        query = request.form['query'] if 'query' in request.form else None
        username = request.form['username'] if 'username' in request.form else None
        sort = request.form['sort'] if 'sort' in request.form else None
        period = request.form['period'] if 'period' in request.form else None

        query_params = {
            "limit": limit,
            "page": page,
            "types": types,
        }

        if tag:
            query_params["tag"] = tag
        if query:
            query_params["query"] = query
        if username:
            query_params["username"] = username
        if sort:
            query_params["sort"] = sort
        if period:
            query_params["period"] = period

        models = fetch_models(query_params)
        
        # 폴더 생성
        if 'username' in query_params:
            folder_name = query_params['username']
        elif 'tag' in query_params:
            folder_name = query_params['tag']
        elif 'query' in query_params:
            folder_name = query_params['query']
        else:
            # 'username', 'tag', 'query' 중 어떤 값도 존재하지 않을 경우의 처리
            folder_name = "default_folder_name"
        os.makedirs(folder_name, exist_ok=True)
        
        # 다운로드 진행 상황 표시를 위한 tqdm 설정
        progress_bar = tqdm(models, desc="Downloading", unit="file")
        download_urls = []

        for model in progress_bar:
            version = model["modelVersions"][0]
            try:
                download_url = version["downloadUrl"]
                download_urls.append(download_url)
            except:
                pass
            print(download_urls)
        for url in download_urls:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                # 파일 이름 가져오기
                content_disposition = response.headers.get("content-disposition")
                if content_disposition:
                    filename = content_disposition.split("filename=")[-1].strip('"')
                else:
                    filename = "downloaded_file"  # 파일 이름을 가져올 수 없는 경우 기본값으로 "downloaded_file"을 사용

                # 파일 저장 경로
                file_path = os.path.join(folder_name, filename)

                # 이미 파일이 존재하는 경우 스킵
                if os.path.exists(file_path):
                    print(f"파일이 이미 존재합니다. 스킵합니다: {file_path}")
                    continue
                else:
                    # 파일 저장
                    with open(file_path, "wb") as file:
                        total_size = int(response.headers.get("content-length", 0))
                        downloaded_size = 0
                        for data in response.iter_content(chunk_size=4096):
                            file.write(data)
                            downloaded_size += len(data)
                            progress_bar.set_postfix({"Progress": f"{downloaded_size}/{total_size} bytes"})

                    progress_bar.set_postfix({"Progress": "Complete"})
                    print(f"다운로드 완료: {file_path}")
            else:
                print(f"파일 다운로드 실패: {url}")
        
        return render_template('results.html', models=models)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
