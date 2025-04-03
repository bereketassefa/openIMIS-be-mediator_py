import graphene
from core.schema import TinyInt, SmallInt, OpenIMISMutation
from .signals import new_claim_from_emr

class ClaimInputType(OpenIMISMutation.Input):
    name = graphene.String(required=True)


class CreateEMRClaim(OpenIMISMutation):
    """
    Create a new claim from EMR
    """
    _mutation_module = "mediator"
    _mutation_class = "CreateEMRClaim"

    class Input(ClaimInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        print(data)
        # new_claim_from_emr.send(
        #      claim = "sample claim"
        # )
        return "this workk"