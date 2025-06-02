import os
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload


class YouTubeUploader:
    def __init__(self, credentials):
        self.scopes = [
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.upload",
        ]
        self.credentials = credentials
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=self.credentials
        )

    def upload_video(
        self,
        video_path,
        title=None,
        description="Description of uploaded video.",
        category_id=20,
        privacy_status="public",
        made_for_kids=False,
        tags=None,
    ):
        if tags is None:
            tags = []
        video_name = os.path.basename(video_path)
        video_title = title if title else os.path.splitext(video_name)[0]
        request_body = {
            "snippet": {
                "categoryId": category_id,
                "description": description,
                "title": video_title,
                "tags": tags,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": made_for_kids,
            },
        }
        media_file = MediaFileUpload(video_path)
        response_upload = (
            self.youtube.videos()
            .insert(
                part="snippet,status",
                body=request_body,
                media_body=media_file,
            )
            .execute()
        )
        return response_upload
