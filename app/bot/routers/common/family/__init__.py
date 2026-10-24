from aiogram import Router
from . import marriage, families, divorce, rename

router = Router()

router.include_router(marriage.router)
router.include_router(families.router)
router.include_router(divorce.router)
router.include_router(rename.router)