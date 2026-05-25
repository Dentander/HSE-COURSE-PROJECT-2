from pydantic import BaseModel, ConfigDict, Field


class DailyCorrectTaskStreakOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    consecutive_days: int = Field(serialization_alias="consecutiveDays")
    is_fire_frozen: bool = Field(serialization_alias="isFireFrozen")
    streak_updated: bool = Field(
        default=False, serialization_alias="streakUpdated"
    )


class TopicStoryTasksProgressOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    topic_id: str = Field(serialization_alias="topicId")
    completed_story_tasks: int = Field(serialization_alias="completedStoryTasks")
    total_story_tasks: int = Field(serialization_alias="totalStoryTasks")


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
