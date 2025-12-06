from flicker.services.proactive.intent_parser.intent import Intent
from pydantic import BaseModel, Field
from typing import Optional, Literal


class AddTodoSchema(BaseModel):
    title: str = Field(description="待办事项标题")
    content: str = Field(description="待办事项内容")
    deadline: Optional[str] = Field(description="截止时间(可选)")


addTodoIntent = Intent(
    name="添加待办事项",
    description="当识别到屏幕上能够体现出用户需要处理的通知、事务或者流量耗尽，"
                "提醒充值等能够推断出用户后续需要进行某些操作的时候，可以触发"
                "待办事项操作",
    parameterSchema=AddTodoSchema
)


class AddExpenseSchema(BaseModel):
    title: str = Field(description="支出标题")
    amount: float = Field(description="支出金额")
    currency: Literal['CNY', 'USD'] = Field(description="货币类型")
    date: Optional[str] = Field(description="支出日期(可选)")


addExpenseIntent = Intent(
    name="记一笔帐",
    description="当识别到屏幕上有与财务相关的信息，比如购物订单、发票、收据等内容时，可以触发记账操作。"
                "但如果是账单，还款通知等汇总信息而非具体支出等情况，不应触发本意图",
    parameterSchema=AddExpenseSchema
)


class AddNoteSchema(BaseModel):
    title: str = Field(description="笔记标题")
    content: str = Field(description="笔记内容")


addNoteIntent = Intent(
    name="添加笔记",
    description="当识别到屏幕上有重要信息需要保存，"
                "比如会议纪要、重要通知等内容时，可以触发添加笔记操作",
    parameterSchema=AddNoteSchema
)
