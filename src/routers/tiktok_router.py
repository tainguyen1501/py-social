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
    Xử lý raw video data thành format đồng bộ
    """
    author_info = raw.get("author", {})
    stats_info = raw.get("stats", {})
    music_info = raw.get("music", {})
    video_info = raw.get("video", {})
    
    clean = {
        # Video Basic Info
        "id": raw.get("id"),
        "description": raw.get("desc"),
        "created_time": raw.get("createTime"),
        "duration": video_info.get("duration"),
        
        # Author Information - Đầy đủ
        "author": {
            # Basic Info
            "id": author_info.get("id"),
            "unique_id": author_info.get("uniqueId"),
            "nickname": author_info.get("nickname"),
            "signature": author_info.get("signature", ""),
            "verified": author_info.get("verified", False),
            "secret": author_info.get("secret", False),
            "ftc": author_info.get("ftc", False),
            
            # Avatar URLs - Đầy đủ kích thước
            # "avatars": {
            #     "thumb": author_info.get("avatarThumb"),
            #     "medium": author_info.get("avatarMedium"),
            #     "large": author_info.get("avatarLarger"),
            # },
            "avatar": author_info.get("avatarMedium"),
            
            # Stats
            "stats": {
                "follower_count": author_info.get("followerCount", 0),
                "following_count": author_info.get("followingCount", 0),
                "heart_count": author_info.get("heartCount", 0),
                "video_count": author_info.get("videoCount", 0),
                "digg_count": author_info.get("diggCount", 0),
            },
            
            # Links
            "links": {
                "profile_url": f"https://www.tiktok.com/@{author_info.get('uniqueId')}",
                "tiktok_profile": f"tiktok.com/@{author_info.get('uniqueId')}",
                # "open_favorite": author_info.get("openFavorite", False),
            },
            
            # Additional
            # "create_time": author_info.get("createTime"),
            # "tt_seller": author_info.get("ttSeller", False),
            # "is_ad_virtual": author_info.get("isADVirtual", False),
        },
        
        # Music Information
        "music": {
            "id": music_info.get("id"),
            "title": music_info.get("title"),
            "author": music_info.get("authorName"),
            "album": music_info.get("album"),
            "duration": music_info.get("duration"),
            "original": music_info.get("original", False),
            "play_url": music_info.get("playUrl"),
            # "cover_large": music_info.get("coverLarge"),
            # "cover_medium": music_info.get("coverMedium"),
            # "cover_thumb": music_info.get("coverThumb"),
        },
        
        # Video Statistics
        "stats": {
            "views": stats_info.get("playCount", 0),
            "likes": stats_info.get("diggCount", 0),
            "comments": stats_info.get("commentCount", 0),
            "shares": stats_info.get("shareCount", 0),
            "saves": stats_info.get("collectCount", 0),
            "reposts": stats_info.get("repostCount", 0),
        },
        
        # Video Details
        "video_details": {
            "duration": video_info.get("duration"),
            "width": video_info.get("width"),
            "height": video_info.get("height"),
            "ratio": video_info.get("ratio"),
            "format": video_info.get("format"),
            "video_quality": video_info.get("videoQuality"),
            
            # Cover Images
            # "covers": {
            #     "cover": video_info.get("cover"),
            #     "origin_cover": video_info.get("originCover"),
            #     "dynamic_cover": video_info.get("dynamicCover"),
            #     "share_cover": video_info.get("shareCover", []),
            # },
            "origin_cover": video_info.get("originCover"),


            # Video URLs
            # "urls": {
            #     "play_addr": video_info.get("playAddr"),
            #     "download_addr": video_info.get("downloadAddr"),
            #     "reflow_cover": video_info.get("reflowCover"),
            # },
            
            # Technical Info
            # "bitrate": video_info.get("bitrate"),
            # "encoded_type": video_info.get("encodedType"),
            # "codec_type": video_info.get("codecType"),
        },
        
        # Important URLs
        # "urls": {
        #     "tiktok_url": f"https://www.tiktok.com/@{author_info.get('uniqueId')}/video/{raw.get('id')}",
        #     "share_url": f"https://vt.tiktok.com/{raw.get('id')}",
        #     "download_url": f"http://127.0.0.1:8000/api/v1/tiktok/download/{raw.get('id')}",
        #     "video_direct_url": video_info.get("playAddr"),
        #     "author_profile_url": f"https://www.tiktok.com/@{author_info.get('uniqueId')}",
        # },
        "tiktok_video_url": f"https://www.tiktok.com/@{author_info.get('uniqueId')}/video/{raw.get('id')}",
        # Additional Metadata
        # "metadata": {
        #     "region": region,
        #     "language": language,
        #     "is_original": raw.get("originalItem", False),
        #     "is_ad": raw.get("isAd", False),
        #     "private_item": raw.get("privateItem", False),
        #     "duet_enabled": raw.get("duetEnabled", True),
        #     "stitch_enabled": raw.get("stitchEnabled", True),
        #     "share_enabled": raw.get("shareEnabled", True),
        # },
        
        # Challenges/Hashtags
        # "challenges": [
        #     {
        #         "id": challenge.get("id"),
        #         "title": challenge.get("title"),
        #         "desc": challenge.get("desc"),
        #         "cover": challenge.get("cover"),
        #         "is_commerce": challenge.get("isCommerce", False),
        #     } for challenge in raw.get("challenges", [])
        # ],
        
        # Text Extra (Mentions, Hashtags)
        # "text_extra": [
        #     {
        #         "type": extra.get("type"),
        #         "text": extra.get("text"),
        #         "user_id": extra.get("userId"),
        #         "hashtag_id": extra.get("hashtagId"),
        #         "hashtag_name": extra.get("hashtagName"),
        #     } for extra in raw.get("textExtra", [])
        # ],
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

@router.get("/download-direct")
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
    


