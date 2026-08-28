from sqlalchemy.ext.asyncio import AsyncSession

class Base:
    def __init__(self, session: AsyncSession):
        self.session = session