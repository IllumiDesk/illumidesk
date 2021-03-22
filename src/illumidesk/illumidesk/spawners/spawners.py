from kubespawner import KubeSpawner
from traitlets.traitlets import Bool


class IllumiDeskKubeSpawner(KubeSpawner):
    """Extends the KubeSpawner by defining the common behavior for our Spwaners that work
    with LTI versions 1.1 and 1.3
    """

    load_shared_folder_with_instructor = Bool(
        True,
        config=True,
        help="Mount the shared folder with Instructor role (Used with shared_folder_enabled env-var).",
    )
