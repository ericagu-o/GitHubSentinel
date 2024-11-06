import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

def chatbot(message, history):
    #  这里需要根据你的LLM类实现具体的聊天逻辑
    response = llm.chat(message, history)  # 使用llm实例进行对话
    return response

# 创建各个标签页的Interface实例
report_interface = gr.Interface(
    fn=export_progress_by_date_range,
    inputs=[
        gr.Dropdown(subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"),
        gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天"),
    ],
    outputs=[gr.Markdown(), gr.File(label="下载报告")],
    title="报告生成"  #  为每个Interface添加标题
)



chatbot_interface = gr.ChatInterface(chatbot, type="messages")


# 使用TabbedInterface组合多个标签页
demo = gr.TabbedInterface([report_interface, chatbot_interface], ["报告生成", "聊天机器人"])
if __name__ == "__main__":
    demo.launch(debug=True)  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))