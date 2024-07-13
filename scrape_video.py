import requests
import json
import re
def scrape_vid(vid_url, n):
    url = 'https://savetwitter.net/api/ajaxSearch'
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
    payload = {
    'q': vid_url,
    'lang': 'en'
    }

    response = requests.post(url, headers=headers, data=payload)

    response_data = json.loads(response.text)

    audio_url_match = re.search(r'data-audioUrl=\"(.*?)\"', response_data['data'])

    if audio_url_match:
        video_url = audio_url_match.group(1)
        # print(video_url)
        output_file = f'downloaded_video{n}.mp4'

        try:
            response = requests.get(video_url, stream=True)

            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            print("Video downloaded successfully as", output_file)
            

        except requests.RequestException as e:
            print("Error downloading the video:", e)