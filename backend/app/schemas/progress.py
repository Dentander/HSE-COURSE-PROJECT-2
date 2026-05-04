from pydantic import BaseModel, Field


class DailyCorrectTaskStreakOut(BaseModel):
    consecutive_days: int = Field(
        description="Число дней подряд с хотя бы одним правильно решённым заданием",
    )


class TopicTasksProgressOut(BaseModel):
    topicId: str
    topicTitle: str
    topicOrder: int
    completedTasks: int
    totalTasks: int


class MyTasksProgressOut(BaseModel):
    topics: list[TopicTasksProgressOut] = Field(
        default_factory=list,
        description="Топики в порядке курса с числом заданий и выполненных",
    )
    completedTasksTotal: int
    totalTasksTotal: int
