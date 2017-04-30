from sqlalchemy import ForeignKey
import sqlalchemy.types as ModelTypes
import sqlalchemy.ext.declarative as _declerative
from sqlalchemy.schema import Column as ModelField
from sqlalchemy.exc import IntegrityError


# export foreign key under types
ModelTypes.ForeignKey = ForeignKey


class _Base(object):
    '''
    Model Base Class.
    
    All models used in the app should inherit from this.
    '''

    # tablename is automatically generated according to the name of the class
    @_declerative.declared_attr
    def __tablename__(cls):
        return '{0}s'.format(cls.__name__.lower())

    # inheriting classes can override this list with the name of fields it should render
    renders_fields = []

    # inheriting classes can override this string with possible reasons for integrity exceptions,
    # so endpoints can catch such exceptions and use this string to describe the possible reasons.
    integrity_fail_reasons = ''

    # all models have an auto-incrementing integer id as primary key
    id = ModelField(ModelTypes.Integer, primary_key=True, autoincrement=True)

    def render(self, **kwargs):
        '''
        Creates a dict representation, which later can be returned to user as json. 
        '''
        output = {}

        for field in self.renders_fields + ['id']:
            field_value = getattr(self, field)
            if hasattr(field_value, 'render') and isinstance(field_value.render, callable):
                output[field] = field_value.render()
            else:
                output[field] = field_value

        return output


Model = _declerative.declarative_base(cls=_Base)
