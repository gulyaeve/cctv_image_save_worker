from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CameraModel(Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(primary_key=True)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"))
    camera_ip: Mapped[str] = mapped_column(nullable=True)
    reg_ip: Mapped[str] = mapped_column(nullable=True)
    view: Mapped[str] = mapped_column(nullable=True)
    rtsp_url: Mapped[str] = mapped_column(nullable=False)
    pos_x: Mapped[int] = mapped_column(nullable=True)
    pos_y: Mapped[int] = mapped_column(nullable=True)
    polygon_map: Mapped[str] = mapped_column(nullable=True)

    classroom = relationship("ClassroomModel", back_populates="cameras")

    def __str__(self) -> str:
        return f"{self.view}"
