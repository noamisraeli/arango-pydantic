from datetime import datetime
from enum import Enum

import pydantic

"""
Models for basic functionality of the site
"""

class BusinessValue(pydantic.BaseModel):
    """
    A representation of the business value.
    The business value is the highest level of value in the business.

    for example:
        money.
        number of clients.
        impacting of the company stack. 

    business can be:
    - software development team, responsible on delivering features to a product.
    - factory responsible on producing medical equipment to pharmacies.
    """
    value: int


class Order(pydantic.BaseModel): # or Process or Higher-level Job ? 
    """
    A representation of a single, independent business value.
    for example:
        Production of a product.
        Delivering of delivery.
        Finishing of the worker shift. (?)
    """
    delivery_time: datetime
    cost: BusinessValue


class PartOf:
    """
    Relationship between job and higher level orders.
    """
    _from: 'Job'
    _to: 'Order'


class JobStatus(Enum):
    NOT_STARTED = 'NOT STARTED'
    IN_PROGRESS = 'IN PROGRESS'
    FINISHED = 'FINISHED'
    

class Job:
    """
    Entity represents a single part of a process.
    Job is executed by a single resource.
    """
    status: JobStatus


class DependsOn:
    """
    dependency between jobs means that the _from job can't start before the _to job is finished.
    """
    _from: Job
    _to: Job


class ExecutedBy:
    """
    Relationship between a job and its resource.

    estimated_execution_time: the amount of time needed for the resource to execute the job.
    for example:
        A single job X can take Y amount of time when executed by resource Z. 
        the same job X can task W != Y amount of time when executed by resource Q. 

    estimated_execution_time_accuracy: the standard deviation of the estimated_execution_time accuracy.
    for example:
        The standard deviation in human resource is much higher then the standard deviation of a machine-resource.

    start_execution_time: the point in time when the job execution is starting.
    """
    _from: Job
    _to: 'Resource'

    estimated_execution_time: datetime
    execution_time_accuracy: float = 1
    
    start_execution_time: datetime
    

class Resource: # Or Executor
    """
    Entity that is able to execute jobs.
    """


"""
Queries:
    get all jobs affected by a job change:
        get all dependent jobs:
            all jobs with a DependsOn INBOUND to the changed job

        get all affected jobs executed by the job's pre-change and after-change resource, with start_time after the job's start_time
            all jobs with ExecutedBy (filter with the start_time>=job.executed_by.start_time) INBOUND relation to the job's resource.

    get current cost of the graph:

    get all valid places for job to be scheduled:
        filter by job type in corelation to the resource supported types.

"""


"""
Components:

"""