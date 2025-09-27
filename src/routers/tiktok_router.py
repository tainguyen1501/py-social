import os
import io
from typing import Optional, cast
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from TikTokApi import TikTokApi
router = APIRouter(prefix="/api/v1/tiktok", tags=["TikTok"])

async def create_tiktok_session(
    user_ms_token: str = "",
    num_sessions: int = 1,
    sleep_after: int = 3,
    browser: Optional[str] = None,
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
        browser=browser,
    )
    return api

def process_video_data(raw: dict, region: str = "VN") -> dict:
    """
    Chuẩn hóa raw TikTok video data thành format đồng bộ
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
        "id": safe_str(raw.get("id")),
        "description": safe_str(raw.get("desc")),
        "created_time": safe_str(raw.get("createTime")),
        "duration": safe_int(video_info.get("duration")),

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

        "music": {
            "id": safe_str(music_info.get("id")),
            "title": safe_str(music_info.get("title")),
            "author": safe_str(music_info.get("authorName")),
            "album": safe_str(music_info.get("album")),
            "duration": safe_int(music_info.get("duration")),
            "original": bool(music_info.get("original", False)),
            "play_url": safe_str(music_info.get("playUrl")),
        },

        "stats": {
            "views": safe_int(stats_info.get("playCount")),
            "likes": safe_int(stats_info.get("diggCount")),
            "comments": safe_int(stats_info.get("commentCount")),
            "shares": safe_int(stats_info.get("shareCount")),
            "saves": safe_str(stats_info.get("collectCount")),
            "reposts": safe_int(stats_info.get("repostCount")),
        },

        "video_details": {
            "duration": safe_int(video_info.get("duration")),
            "width": safe_int(video_info.get("width")),
            "height": safe_int(video_info.get("height")),
            "ratio": safe_str(video_info.get("ratio")),
            "format": safe_str(video_info.get("format")),
            "video_quality": safe_str(video_info.get("videoQuality")),
            "origin_cover": safe_str(video_info.get("originCover")),
        },

        "tiktok_video_url": safe_str(
            f"https://www.tiktok.com/@{author_info.get('uniqueId')}/video/{raw.get('id')}"
        ),
    }

    return clean


def get_api(request: Request):
    api = getattr(request.app.state, "tiktok_api", None)
    if not api:
        raise HTTPException(status_code=500, detail="TikTok session not initialized")
    return api


@router.get("/video-info")
async def video_info(request: Request, url: str = Query(..., description="TikTok video URL")):
    api = get_api(request)
    video = api.video(url=url)
    video_data = await video.info()
    return process_video_data(video_data)


@router.get("/download-video")
async def download_video_direct(request: Request, url: str = Query(..., description="TikTok video URL")):
    try:
        api = get_api(request)
        video = api.video(url=url)
        video_info = await video.info()
        video_bytes = cast(bytes, await video.bytes())
        return StreamingResponse(
            io.BytesIO(video_bytes),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename=tiktok_{video_info['id']}.mp4"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/trendings")
async def trendings(
    request: Request,
    count: int = Query(5, ge=1, le=10, description="Số lượng video (1-10)"),
    region: str = Query("VN", description="Mã quốc gia (VN, US, etc.)"),
    language: str = Query("vi", description="Ngôn ngữ (vi, en, etc.)"),
):
    """
    Lấy danh sách video trending
    """
    try:
        api = get_api(request)
        results = []
        async for video in api.trending.videos(count=count, custom_region=region.upper()):
            raw = video.as_dict
            clean = process_video_data(raw, region=region)
            results.append(clean)

        return {
            "region": region,
            "language": language,
            "total_count": len(results),
            "videos": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
