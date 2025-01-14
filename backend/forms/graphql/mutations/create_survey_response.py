import graphene
from graphene.types.generic import GenericScalar

from core.utils import get_ip

from ...models.response import Response
from ...models.survey import Survey
from ..form_response import FullResponseType


class CreateSurveyResponse(graphene.Mutation):
    class Arguments:
        event_slug = graphene.String(required=True)
        survey_slug = graphene.String(required=True)
        form_data = GenericScalar(required=True)
        locale = graphene.String()

    response = graphene.Field(FullResponseType)

    @staticmethod
    def mutate(
        root,
        info,
        event_slug: str,
        survey_slug: str,
        form_data: str,
        locale: str = "",
    ):
        survey = Survey.objects.get(event__slug=event_slug, slug=survey_slug)

        if not survey.is_active:
            raise Exception("Survey is not active")

        form = survey.get_form(locale)

        ip_address = get_ip(info.context)
        created_by = user if (user := info.context.user) and user.is_authenticated else None

        response = Response.objects.create(
            form=form,
            form_data=form_data,
            created_by=created_by,
            ip_address=ip_address,
        )

        return CreateSurveyResponse(response=response)  # type: ignore
