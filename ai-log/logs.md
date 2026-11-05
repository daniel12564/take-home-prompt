# AI logs

# plan_refinement

This log has the interaction after I defined the "initial" version of the implementation plan on [`PLAN.md`](PLAN.md). Here I used the skill `grill-with-docs` to help me improve and take in consideration all the missing points that I didn't take into consideration in the first plan. Also used the skills `to-spec` and `to-tickets` to translate all the previous work into documents that can later be used by other agents that will do the real implementation of the plan.
For this kind of task where I need a strong and incisive review partner I use the model of Fable 5.1.
In general here is the part where I try to modify or reject the proposals that the model presents via their questions. In specific I proposed a different approach on how to populate the database using something less complex and more straightforward as creating csv files and using custom Django commands.

# implementations

This log contains mostly the whole implementation process of the agent for all the tasks that where defined with the previous agent. Here I used the skill `implement-spec`. When a task has multiple subtasks, I usually like to run the first tasks one by one and do some validations. If all works well I let the agent complete the remaining tasks. After all is completed I do manuals validations to test that the whole application is working as expected, also use the checklist of the task itself.
For this tasks that involves the process of writting code itself I use more lighter models like Sonnet 5.5.