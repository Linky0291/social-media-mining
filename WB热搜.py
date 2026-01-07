import csv
import os
import time
from datetime import datetime
from DrissionPage import ChromiumPage

def main():
    # 1. 配置保存路径
    save_dir = r"D:/python_Lin/爬虫学习实习/爬虫/文件保存放这里"
    
    # 确保目录存在，如果不存在则创建
    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
            print(f"📁 已创建保存目录: {save_dir}")
        except Exception as e:
            print(f"❌ 创建目录失败: {e}")
            print("⚠️  将使用当前目录保存文件")
            save_dir = "."  # 失败时使用当前目录
    
    # 2. 启动浏览器
    print("🔥 正在启动 DrissionPage...")
    page = ChromiumPage()
    
    # 3. 访问微博热搜
    url = 'https://s.weibo.com/top/summary'
    print(f"🔗 正在访问: {url}")
    page.get(url)
    time.sleep(3)  # 添加等待确保页面加载
    
    # ================= 智能等待与人工介入 =================
    # 使用 page.ele() 而不是 page.wait.ele() 来查找元素
    # 'css:td.td-02' 是热搜标题所在的单元格
    element = page.ele('css:td.td-02', timeout=10)
    if not element:
        print("\n" + "!"*50)
        print("⚠️ 检测到页面未加载或显示白屏（可能是触发了验证或网络卡顿）")
        print("👉 请现在手动在浏览器中操作：刷新页面 或 扫码登录")
        print("👉 确认能看到热搜列表后，请在下方按【回车键】继续程序...")
        print("!"*50 + "\n")
        input("WAITING: 操作完成后，请按回车继续 >> ")
        # 手动操作后再次尝试查找
        element = page.ele('css:td.td-02', timeout=10)
        if not element:
            print("❌ 依然未获取到内容，请检查网站是否改版或IP被封禁。")
            return
    
    # ====================================================

    # 4. 开始解析数据
    # 获取所有的行（每一行是一个热搜）
    rows = page.eles('css:tbody tr')
    
    if not rows:
        print("❌ 未获取到热搜行数据，请检查选择器是否正确。")
        return

    print(f"✅ 成功获取页面，包含 {len(rows)} 个条目，开始解析...\n")

    # 准备数据列表
    data_list = []
    
    print("-" * 80)
    print(f"{'排名':<6} | {'热度':<10} | 标题")
    print("-" * 80)

    for row in rows:
        try:
            # --- 解析排名 ---
            rank_ele = row.ele('css:td.td-01')
            if not rank_ele:
                continue  # 跳过没有排名元素的行
                
            rank = rank_ele.text.strip()
            if not rank:
                rank = "置顶"  # 处理置顶微博没有数字排名的情况

            # --- 解析标题和链接 ---
            title_ele = row.ele('css:td.td-02 a')
            if not title_ele:
                continue  # 跳过没有标题的行
                
            title = title_ele.text.strip()
            link = title_ele.attr('href')
            if link and link.startswith('/'):
                link = f"https://s.weibo.com{link}"
            elif not link:
                link = "N/A"

            # --- 解析热度 ---
            hot_ele = row.ele('css:td.td-02 span')
            hot_val = hot_ele.text.strip() if hot_ele else "N/A"

            # 打印到控制台
            print(f"{rank:<6} | {hot_val:<10} | {title}")

            # 添加到数据列表
            data_list.append([rank, title, hot_val, link])

        except Exception as e:
            # 防止某一行解析失败导致整个程序崩溃
            print(f"解析行时出错: {e}")
            continue

    print("-" * 80)

    # 5. 保存到 CSV 文件
    if data_list:  # 只有有数据时才保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"weibo_hot_{timestamp}.csv"
        filepath = os.path.join(save_dir, filename)
        
        try:
            with open(filepath, mode='w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['排名', '标题', '热度', '链接'])  # 表头
                writer.writerows(data_list)
            
            print(f"\n🎉 抓取成功！")
            print(f"📂 文件已保存到: {filepath}")
            print(f"📊 共保存 {len(data_list)} 条数据")
            
            # 显示目录中已有的微博热搜文件
            show_existing_files(save_dir)
            
        except PermissionError:
            print(f"❌ 权限拒绝：无法写入文件 {filepath}")
            print("👉 请关闭可能正在使用该文件的程序（如Excel），或检查文件权限")
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
    else:
        print("\n⚠️ 未抓取到任何有效数据，请检查页面结构是否已变化。")

def show_existing_files(directory):
    """显示指定目录中已有的微博热搜文件"""
    try:
        # 获取目录中所有的.csv文件
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv') and 'weibo_hot' in f]
        
        if csv_files:
            print(f"\n📋 当前目录已有 {len(csv_files)} 个微博热搜文件:")
            csv_files.sort(reverse=True)  # 按文件名倒序排列（最新的在前）
            for i, file in enumerate(csv_files[:5], 1):  # 显示最新的5个文件
                file_size = os.path.getsize(os.path.join(directory, file))
                print(f"  {i}. {file} ({file_size/1024:.1f} KB)")
            
            if len(csv_files) > 5:
                print(f"  ... 还有 {len(csv_files)-5} 个文件")
        else:
            print(f"\n📋 当前目录中暂无微博热搜文件")
            
    except Exception as e:
        print(f"⚠️ 无法列出目录文件: {e}")

if __name__ == "__main__":
    main()