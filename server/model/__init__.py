import sqlalchemy.types as ModelTypes
import sqlalchemy.ext.declarative as _declerative
from sqlalchemy.schema import Column as ModelField


class _Base(object):

    @_declerative.declared_attr
    def __tablename__(cls):
        return '{0}s'.format(cls.__name__.lower())

    id = ModelField(ModelTypes.Integer, primary_key=True, autoincrement=True)


Model = _declerative.declarative_base(cls=_Base)
