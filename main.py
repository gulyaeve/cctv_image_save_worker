import asyncio
import logging
import aio_pika
from faststream import FastStream
from app.camera_utils.streaming import Camera
from app.cameras.dao import CamerasDAO
from app.schemas import IncidentFullInfo
from app.settings import settings
from faststream.rabbit import RabbitBroker, RabbitQueue, ExchangeType, RabbitExchange


# Настройка логирования
logging.basicConfig(level=logging.INFO)


queue = RabbitQueue(settings.QUEUE_NAME, auto_delete=False)
exchange_out = RabbitExchange(settings.EXCHANGE_NAME_OUTPUT, ExchangeType.FANOUT)
exchange_in = RabbitExchange(settings.EXCHANGE_NAME_INPUT, ExchangeType.DIRECT)
broker = RabbitBroker(url=settings.rabbitmq_url)
app = FastStream(broker)


@broker.subscriber(queue, exchange_in)
async def incident_scr_handler(incident: IncidentFullInfo):
    logging.info(incident)
    screenshot_dir = "/screenshots"

    if incident.cameras_ids:
        # Save screenshots to disk
        for camera, filename in zip(incident.cameras_ids, incident.cameras_screenshots):
            camera_data = await CamerasDAO.find_one_or_none(id=camera)
            if camera_data:
                camera_rtsp = camera_data.rtsp_url
                frame = Camera(camera_rtsp)
                frame.save_screenshot(f"{screenshot_dir}/{filename}")

    # async with broker:
    await broker.publish(
        incident,
        exchange=settings.EXCHANGE_NAME_OUTPUT
    )
    


async def main():
    async with broker:
        img_queue: aio_pika.RobustQueue = await broker.declare_queue(queue)
        img_exchange: aio_pika.RobustExchange = await broker.declare_exchange(exchange_in)
        await img_queue.bind(exchange=img_exchange)

        await broker.declare_exchange(exchange_out)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
