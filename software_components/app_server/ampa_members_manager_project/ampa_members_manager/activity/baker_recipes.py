from model_bakery.recipe import Recipe, foreign_key

from ampa_members_manager.activity.models.repetitive_activity import RepetitiveActivity
from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity.models.unique_activity import UniqueActivity
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration

unique_activity_local_recipe = Recipe(UniqueActivity)
repetitive_activity_local_recipe = Recipe(RepetitiveActivity)

single_activity_with_unique_activity_local_recipe = Recipe(
    SingleActivity, unique_activity=foreign_key(unique_activity_local_recipe))

single_activity_with_repetitive_activity_local_recipe = Recipe(
    SingleActivity, repetitive_activity=foreign_key(repetitive_activity_local_recipe))

activity_registration_with_single_activity_local_recipe = Recipe(
    ActivityRegistration, single_activity=foreign_key(single_activity_with_unique_activity_local_recipe))
