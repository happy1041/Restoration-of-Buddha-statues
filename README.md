全程 vibe coding，应该没有很特别的 requirement，直接 python main.py 运行即可

使用 api：[https://api.aabao.vip]（调用要改成 top）

gemini-3-pro-image-preview+sora-2-landscape-15s

这个网站的 sora-2-pro 大概是用不了的，我认为这是目前最好的工作流方案，当然可以中间插入新环节用来 prompt enginring

to do：

- 背景+更好的视频质量 prompt enginring
  - 背景彩绘 ok
  - 但是小佛像也许难搞，还没搞
  - 并非一定是静音的
- 视频的异步生成概率 fail，现在是单独写的一个 resume_task.py 来重新获取到任务。
  - 600ms time limit
- 多任务同时生成（看看网站的文档）