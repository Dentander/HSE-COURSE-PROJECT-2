from pydantic import BaseModel, Field


class DailyCorrectTaskStreakOut(BaseModel):
    consecutive_days: int


class TopicTasksProgressOut(BaseModel):
    topicId: str
    topicTitle: str
    topicOrder: int
    completedTasks: int
    totalTasks: int


class MyTasksProgressOut(BaseModel):
    topics: list[TopicTasksProgressOut] = Field(default_factory=list)
    completedTasksTotal: int
    totalTasksTotal: int
