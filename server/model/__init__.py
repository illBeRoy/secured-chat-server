import sqlalchemy.types as ModelTypes
import sqlalchemy.ext.declarative as _declerative
from sqlalchemy.schema import Column as ModelField
from sqlalchemy.exc import IntegrityError


class _Base(object):
    '''
    Model Base Class.
    
    All models used in the app should inherit from this.
    '''

    # tablename is automatically generated according to the name of the class
    @_declerative.declared_attr
    def __tablename__(cls):
        return '{0}s'.format(cls.__name__.lower())

    # an inheriting class can override this list with the name of fields it should render
    renders_fields = []

    # all models have an auto-incrementing integer id as primary key
    id = ModelField(ModelTypes.Integer, primary_key=True, autoincrement=True)

    def render(self, **kwargs):
        '''
        Creates a dict representation, which later can be returned to user as json. 
        '''
        output = {}

        for field in self.renders_fields + ['id']:
            output[field] = getattr(self, field)

        return output


Model = _declerative.declarative_base(cls=_Base)
