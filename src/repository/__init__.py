from .contacts import (
    create_contact,
    get_all_contacts,
    delete_contact,
    update_contact,
    is_upcoming_birthday,
    get_upcoming_birthdays,
)

from .users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    get_user_by_reset_token,
    update_avatar,
    save_reset_token
)

from .cloudinary import (
    upload_to_cloudinary,
    update_user_avatar,
)