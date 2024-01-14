# from aiogram.utils import executor
# from initial import dp, bot
# import config
# import os
# from handlers import handler_register
# import handlers
# from sqlalchemy.orm import DeclarativeBase


# async def on_startup(dp):
#     #await bot.set_webhook(config.URL_APP)
#     pass

# async def on_shutdown(dp):
#     await bot.delete_webhook()
#     handlers.mycursor.close()
#     handlers.db.close()



# handler_register(dp)


# # executor.start_webhook(
# #     dispatcher=dp,
# #     webhook_path="",
# #     on_startup=on_startup,
# #     on_shutdown=on_shutdown,
# #     skip_updates=True,
# #     host="0.0.0.0",
# #     port=int(os.environ.get("PORT", 5000)),
# # )

# executor.start_polling(
#     dispatcher=dp,
#     skip_updates=True,
#     on_startup=on_startup,
#     host="0.0.0.0",
#     port=int(os.environ.get("PORT", 5000)),
# )