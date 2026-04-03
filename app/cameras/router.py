from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, Query, status

from app.broker_utils.camera_broker import camera_broker_sender
from app.cameras.dao import CamerasDAO
from app.cameras.schemas import CameraAddScheme, CameraScheme, CameraSearch
from app.exceptions import ObjectMissingException
from app.users.dependencies import permission_required


router = APIRouter(
    prefix="/cameras",
    tags=["Камеры"],
    dependencies=[Depends(permission_required("cameras"))]
)


@router.post("/run_streams")
async def run_all_streams():
    cameras = await CamerasDAO.find_all()
    for camera in cameras:
        await camera_broker_sender(
            CameraScheme.model_validate(camera),
            "add"
        )


@router.delete("/delete_streams")
async def delete_all_streams():
    cameras = await CamerasDAO.find_all()
    for camera in cameras:
        await camera_broker_sender(
            CameraScheme.model_validate(camera),
            "remove"
        )


@router.get("", response_model=Sequence[CameraScheme])
# @cache(expire=60)
async def get_all_cameras(filter_query: Annotated[CameraSearch, Query()]):
    """
    Get all cameras
    """
    filter_model = filter_query.model_dump(exclude_unset=True, exclude_defaults=True)
    return await CamerasDAO.find_all(**filter_model)


@router.get("/videowall", response_model=Sequence[Sequence[CameraScheme]])
async def get_data_for_videowall(chunk_size: int = 9):
    """
    Получения матрицы камер для видеостены
    :chunk_size: размер чанка, по умолчанию 9
    """
    cameras = await CamerasDAO.find_all()
    chunks = [cameras[i:i+chunk_size] for i in range(0, len(cameras), chunk_size)]
    return chunks


@router.get("/{id}", response_model=CameraScheme)
async def get_camera(id: int):
    camera = await CamerasDAO.find_one_or_none(id=id)
    if camera is None:
        raise ObjectMissingException
    else:
        return camera


@router.post(
    "",
    response_model=CameraScheme,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permission_required("camera_create"))]
)
async def add_camera(data: CameraAddScheme):
    """
    Add camera
    """
    new_object = await CamerasDAO.add(
        **data.model_dump()
    )
    if new_object is None:
        raise ObjectMissingException
    else:
        await camera_broker_sender(
            CameraScheme.model_validate(new_object),
            "add"
        )
        return new_object


# @router.post(
#     "/bulk",
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(permission_required("camera_create"))]
# )
# async def bulk_add_cameras(items: Sequence[CameraAddScheme]) -> Sequence[CameraScheme]:
#     return await CamerasDAO.add_bulk([item.model_dump() for item in items])


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(permission_required("camera_delete"))]
)
async def del_camera(id: int):
    """
    Удалить camera
    """
    existing_object = await CamerasDAO.find_one_or_none(id=id)
    if existing_object is None:
        raise ObjectMissingException
    else:
        await camera_broker_sender(
            CameraScheme.model_validate(existing_object),
            "remove"
        )
        return await CamerasDAO.delete(id=id)


@router.put(
    "/{id}",
    response_model=CameraScheme,
    dependencies=[Depends(permission_required("camera_create"))]
)
async def update_camera(id: int, data: CameraAddScheme):
    """
    update camera
    """
    existing_object = await CamerasDAO.find_one_or_none(id=id)
    if existing_object is None:
        raise ObjectMissingException
    else:
        updated_object = await CamerasDAO.update(id, **data.model_dump())
        await camera_broker_sender(
            CameraScheme.model_validate(updated_object),
            "update"
        )
        return updated_object
    
