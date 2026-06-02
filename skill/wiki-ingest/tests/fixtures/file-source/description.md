# File Source Fixture

## 输入描述

一个模拟的本地文件源，用于测试 wiki-ingest 从文件读取内容并创建 wiki 页面的流程。

## 源内容

**文件路径**: `raw/test-document.md`

**内容**:

```markdown
# 设计模式概述

本文介绍三种常见的设计模式：单例模式、工厂模式和观察者模式。

## 单例模式

确保一个类只有一个实例，并提供全局访问点。

## 工厂模式

定义一个创建对象的接口，让子类决定实例化哪个类。

## 观察者模式

定义对象间的一对多依赖关系，当一个对象状态改变时，所有依赖者都会收到通知。
```

## 预期输出

- 创建页面: `wiki/pages/design-patterns-overview.md`
- 可能创建子页面: `wiki/pages/singleton-pattern.md`, `wiki/pages/factory-pattern.md`, `wiki/pages/observer-pattern.md`
- index.md 中新增条目
- log.md 中追加记录
