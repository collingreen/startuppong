
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


#######################
# MODELS
#######################

class StandardPermission(models.Model):
    """An extremely basic base class for implementing object permission.
    The default implementation requires the model to have a user field
    (foreign key or onetoonefield) and allows permission if the user
    being checked either matches the user field or if the user being
    checked is a staff member.

    Extend the check_permission function as necessary to implement more
    elaborate functionality like group managers or multi-user accounts.

    Usage:
        good_user = User.objects.get(name='owner_user')
        bad_user = User.objects.get(name='random_account')

        object_with_permissions.check_permission(good_user)
        >>> True
        object_with_permissions.check_permission(bad_user)
        >>> False

    """
    class Meta:
        abstract = True

    _permission_type = 'standard'

    # your models need one of these fields
    # user = models.ForeignKey(User)
    # user = models.OneToOneField(User)

    def check_permission(self, user):
        return user == self.user or user.is_staff


#######################
# FUNCTIONS
#######################

def naive_downcast(model_instance):
    """Downcasts a vanilla model instance. If not a subtype, returns the
    model_instance. CAUTION: Each test hits the database! Worst case will run
    a query for every subtype of the model class. If you need to use this often
    or on more than one instance at a time or on a model with lots of subclasses
    look into deeper options like
    https://github.com/carljm/django-model-utils#inheritancemanager."""

    # get app for model
    app_label = model_instance._meta.app_label

    # get other models from app
    app_models = models.get_models(models.get_app(app_label))

    # go through all the models
    for model in app_models:
        # if model is a subclass of the given instance's class
        if model_instance.__class__ in model._meta.parents:
            if hasattr(model_instance, model.__name__.lower()):
                # test database for this instance
                try:
                    return getattr(model_instance, model.__name__.lower())
                except ObjectDoesNotExist:
                    pass

    # didnt find anything, assume fully downcasted
    return model_instance

def listingmanager_downcast(model_instance):
    """Downcasts a model instance that is part of a model with objects
    set to inheritancemanager as defined in django-model-utils
    https://github.com/carljm/django-model-utils#inheritancemanager."""
    return model_instance.__class__.objects.get_subclass(id=model_instance.id)