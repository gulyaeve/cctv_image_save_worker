from app.cameras.models import CameraModel
from app.dao.base import BaseDAO


class CamerasDAO(BaseDAO):
    model = CameraModel
