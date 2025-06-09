from setuptools import setup, find_packages

setup(
    name="tutor-bulk-user-upload",
    version="1.0.0",
    description="Bulk user upload plugin for Open edX",
    packages=find_packages(),
    install_requires=[
        "tutor>=14.0.0",
        "pandas>=1.3.0",
        "celery>=5.0.0",
    ],
    entry_points={
        "tutor.plugin.v1": [
            "bulk_user_upload = tutorbulkuserupload.plugin"
        ]
    },
    package_data={
        'tutorbulkuserupload': ['patches/*', 'templates/*'],
        'bulk_user_upload': ['templates/**/*'],
    },
    include_package_data=True,
)
