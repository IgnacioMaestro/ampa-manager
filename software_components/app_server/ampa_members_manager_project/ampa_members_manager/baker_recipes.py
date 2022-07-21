from model_bakery.recipe import Recipe, foreign_key

from ampa_members_manager.activity.models.repetitive_activity import RepetitiveActivity
from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity.models.unique_activity import UniqueActivity
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration

unique_activity = Recipe(UniqueActivity)
repetitive_activity = Recipe(RepetitiveActivity)

__single_activity_with_unique_activity = Recipe(SingleActivity, unique_activity=foreign_key(unique_activity))
single_activity_with_unique_activity = 'ampa_members_manager.__single_activity_with_unique_activity'

__single_activity_with_repetitive_activity = Recipe(SingleActivity,
                                                    repetitive_activity=foreign_key(repetitive_activity))
single_activity_with_repetitive_activity = 'ampa_members_manager.__single_activity_with_repetitive_activity'

__activity_registration_with_single_activity = Recipe(
    ActivityRegistration, single_activity=foreign_key(single_activity_with_unique_activity))
activity_registration_with_single_activity = 'ampa_members_manager.__activity_registration_with_single_activity'
