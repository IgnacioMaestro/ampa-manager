from model_bakery.recipe import Recipe, foreign_key

from ampa_members_manager.activity.models.repetitive_activity import RepetitiveActivity
from ampa_members_manager.activity.models.activity_payable_part import ActivityPayablePart
from ampa_members_manager.activity.models.unique_activity import UniqueActivity
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration

unique_activity_local_recipe = Recipe(UniqueActivity)
repetitive_activity_local_recipe = Recipe(RepetitiveActivity)

payable_part_with_unique_activity_local_recipe = Recipe(
    ActivityPayablePart, unique_activity=foreign_key(unique_activity_local_recipe))

payable_part_with_repetitive_activity_local_recipe = Recipe(
    ActivityPayablePart, repetitive_activity=foreign_key(repetitive_activity_local_recipe))

activity_registration_with_payable_part_local_recipe = Recipe(
    ActivityRegistration, payable_part=foreign_key(payable_part_with_unique_activity_local_recipe))
