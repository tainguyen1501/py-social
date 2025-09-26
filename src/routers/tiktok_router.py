import os
from typing import Optional
from TikTokApi import TikTokApi
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import io

load_dotenv(".env.local")

router = APIRouter(prefix="/api/v1/tiktok", tags=["DbConnections"])
def process_video_data(raw: dict, region: str = "VN") -> dict:
    """
    Xử lý raw video data thành format đồng bộ và cast kiểu dữ liệu
    """
    author_info = raw.get("author", {})
    stats_info = raw.get("stats", {})
    music_info = raw.get("music", {})
    video_info = raw.get("video", {})

    def safe_str(val):
        return str(val) if val is not None else ""

    def safe_int(val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return 0

    clean = {
        # Video Basic Info
        "id": safe_str(raw.get("id")),
        "description": safe_str(raw.get("desc")),
        "created_time": safe_str(raw.get("createTime")),
        "duration": safe_int(video_info.get("duration")),

        # Author Information
        "author": {
            "id": safe_str(author_info.get("id")),
            "unique_id": safe_str(author_info.get("uniqueId")),
            "nickname": safe_str(author_info.get("nickname")),
            "signature": safe_str(author_info.get("signature")),
            "verified": bool(author_info.get("verified", False)),
            "secret": bool(author_info.get("secret", False)),
            "ftc": bool(author_info.get("ftc", False)),
            "avatar": safe_str(author_info.get("avatarMedium")),
            "stats": {
                "follower_count": safe_int(author_info.get("followerCount")),
                "following_count": safe_int(author_info.get("followingCount")),
                "heart_count": safe_int(author_info.get("heartCount")),
                "video_count": safe_int(author_info.get("videoCount")),
                "digg_count": safe_int(author_info.get("diggCount")),
            },
            "links": {
                "profile_url": safe_str(f"https://www.tiktok.com/@{author_info.get('uniqueId')}"),
                "tiktok_profile": safe_str(f"tiktok.com/@{author_info.get('uniqueId')}"),
            },
        },

        # Music Information
        "music": {
            "id": safe_str(music_info.get("id")),
            "title": safe_str(music_info.get("title")),
            "author": safe_str(music_info.get("authorName")),
            "album": safe_str(music_info.get("album")),
            "duration": safe_int(music_info.get("duration")),
            "original": bool(music_info.get("original", False)),
            "play_url": safe_str(music_info.get("playUrl")),
        },

        # Video Statistics
        "stats": {
            "views": safe_int(stats_info.get("playCount")),
            "likes": safe_int(stats_info.get("diggCount")),
            "comments": safe_int(stats_info.get("commentCount")),
            "shares": safe_int(stats_info.get("shareCount")),
            "saves": safe_str(stats_info.get("collectCount")),
            "reposts": safe_int(stats_info.get("repostCount")),
        },

        # Video Details
        "video_details": {
            "duration": safe_int(video_info.get("duration")),
            "width": safe_int(video_info.get("width")),
            "height": safe_int(video_info.get("height")),
            "ratio": safe_str(video_info.get("ratio")),
            "format": safe_str(video_info.get("format")),
            "video_quality": safe_str(video_info.get("videoQuality")),
            "origin_cover": safe_str(video_info.get("originCover")),
        },

        # Important URLs
        "tiktok_video_url": safe_str(f"https://www.tiktok.com/@{author_info.get('uniqueId')}/video/{raw.get('id')}"),
    }

    return clean

async def create_tiktok_session(
    user_ms_token: str = "",
    num_sessions: int = 1,
    sleep_after: int = 3,
    browser: Optional[str] = None
) -> TikTokApi:
    """
    Tạo và trả về TikTokApi session
    """
    if browser is None:
        browser = os.getenv("TIKTOK_BROWSER", "chromium")
    
    api = TikTokApi()
    await api.create_sessions(
        ms_tokens=[user_ms_token],
        num_sessions=num_sessions,
        sleep_after=sleep_after,
        browser=browser
    )
    return api

@router.get("/video-info")
async def video_info(url: str = Query(..., description="TikTok video URL")):
    api = await create_tiktok_session()
    video = api.video(url=url)
    video_data = await video.info()
    return process_video_data(video_data)

@router.get("/download-video")
async def download_video_direct(url: str = Query(..., description="TikTok video URL")):
    try:
        api = await create_tiktok_session()
        print("1. Đã tạo session thành công")
        # Tạo video object
        video = api.video(url=url)
        print("2. Đã tạo video object")
        
        # Thử lấy info trước
        video_info = await video.info()
        print("3. Đã lấy video info:", video_info.get("id"))
        
        # Thử lấy bytes
        video_bytes = await video.bytes()
        print("4. Đã lấy video bytes, kích thước:", len(video_bytes)) # type: ignore
        
        return StreamingResponse(
            io.BytesIO(video_bytes), # type: ignore
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename=tiktok_{video_info['id']}.mp4"
            }
        )
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(error_details)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# async def trending_videos(count: int = 10):
#     results = []
#     async with TikTokApi() as api:  # type: ignore
#         # ms_token = "4rmnq_lGF3HqWVhSJs4y-2acEpfdtKBIWil6kDCNImZPqYrJQHGCrCrwGJTz_0Gh1EBTfnF4cCt47ZwhBs7A7k8MBQil9GmurTc4bF0kAFrl-ZrsGmxjj2hJL0MXrQCO2Z35d3CwKHRSROc="
#         ms_token = ""
#         await api.create_sessions(
#             ms_tokens=[ms_token],
#             num_sessions=1,
#             sleep_after=3,
#             browser=os.getenv("TIKTOK_BROWSER", "chromium")
#         )
#         async for video in api.trending.videos(count=count):
#             # results.append(video.as_dict)
#             raw = video.as_dict
#             clean = {
#                 "author": {
#                     "id": raw.get("author", {}).get("id"),
#                     "nickname": raw.get("author", {}).get("nickname"),
#                     "avatar": raw.get("author", {}).get("avatarThumb"),
#                 },
#                 "music": {
#                     "title": raw.get("music", {}).get("title"),
#                     "authorName": raw.get("music", {}).get("authorName"),
#                 },
#                 "stats": {
#                     "playCount": raw.get("stats", {}).get("playCount"),
#                     "likeCount": raw.get("stats", {}).get("diggCount"),
#                     "commentCount": raw.get("stats", {}).get("commentCount"),
#                     "shareCount": raw.get("stats", {}).get("shareCount"),
#                 },
#                 "video": {
#                     "url": (
#                         raw.get("video", {})
#                         .get("PlayAddrStruct", {})
#                         .get("UrlList", [None])[0]
#                     ),
#                     "width": raw.get("video", {}).get("width"),
#                     "height": raw.get("video", {}).get("height"),
#                     "duration": raw.get("video", {}).get("duration"),
#                 },
#             }
#             results.append(clean)

#     return results

# @router.get("/trendings")
# async def trendings():
#     videos = await trending_videos()
#     return {
#         "message": "TikTok trending videos fetched successfully",
#         "videos": videos
#     }




@router.get("/trendings")
async def trendings(
    count: int = Query(5, ge=1, le=10, description="Số lượng video (1-10)"),  # Max = 10
    region: str = Query("VN", description="Mã quốc gia (VN, US, etc.)"),
    language: str = Query("vi", description="Ngôn ngữ (vi, en, etc.)")
):
    """
    Lấy danh sách video trending với đầy đủ thông tin user
    """
    try:
        results = []
        api = await create_tiktok_session()
        custom_params = {
            "count": count,
            "custom_region": region.upper()
        }
            
        async for video in api.trending.videos(**custom_params):
            raw = video.as_dict
            clean = process_video_data(raw, region=region)
            results.append(clean)
        return {
            "region": region,
            "language": language,
            "total_count": len(results),
            "videos": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    


