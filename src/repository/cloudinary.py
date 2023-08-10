import cloudinary
import cloudinary.uploader

from fastapi import UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from repository import update_avatar
from conf import settings
from database import User

def upload_to_cloudinary(file: UploadFile, current_user: User):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    r = cloudinary.uploader.upload(
        file.file, public_id=f"ContactsApp/{current_user.username}", overwrite=True
    )

    src_url = cloudinary.CloudinaryImage(
        f"ContactsApp/{current_user.username}"
    ).build_url(width=250, height=250, crop="fill", version=r.get("version"))
    return src_url


async def update_user_avatar(src_url: str, current_user: User, session: AsyncSession):
    user = await update_avatar(current_user.email, src_url, session)
    return user
