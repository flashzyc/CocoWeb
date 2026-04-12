"""运行前检查脚本 - 检查环境是否就绪"""

import sys
from pathlib import Path


def check_python_version():
    """检查 Python 版本"""
    if sys.version_info < (3, 8):
        print("❌ Python 版本过低，需要 3.8+")
        return False
    print(f"✅ Python 版本: {sys.version.split()[0]}")
    return True


def check_dependencies():
    """检查依赖包"""
    required = {
        'rumps': 'rumps',
        'openai': 'openai',
        'playwright': 'playwright',
        'pydantic': 'pydantic',
        'yaml': 'pyyaml'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing.append(package)
    
    return len(missing) == 0, missing


def check_config():
    """检查配置文件"""
    config_file = Path("config/config.yaml")
    example_file = Path("config/config.yaml.example")
    
    if config_file.exists():
        print("✅ 配置文件存在: config/config.yaml")
        # 检查是否配置了 API 密钥
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            api_key = config.get("openai", {}).get("api_key", "")
            if api_key and api_key != "your-api-key-here":
                print("✅ API 密钥已配置")
                return True
            else:
                print("⚠️  API 密钥未配置，请编辑 config/config.yaml")
                return False
    elif example_file.exists():
        print("⚠️  配置文件不存在，但找到示例文件")
        print("   请运行: cp config/config.yaml.example config/config.yaml")
        print("   然后编辑 config/config.yaml 填入 API 密钥")
        return False
    else:
        print("❌ 配置文件不存在")
        return False


def check_directories():
    """检查必要的目录"""
    dirs = ["logs", "logs/runtime", "logs/sessions"]
    all_ok = True
    
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ 目录存在: {dir_path}")
        else:
            print(f"⚠️  目录不存在: {dir_path}（将自动创建）")
            path.mkdir(parents=True, exist_ok=True)
    
    return True


def main():
    """主检查函数"""
    print("=" * 50)
    print("运行环境检查")
    print("=" * 50)
    
    all_ok = True
    
    # 检查 Python 版本
    print("\n1. Python 版本检查")
    if not check_python_version():
        all_ok = False
    
    # 检查依赖
    print("\n2. 依赖包检查")
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        all_ok = False
        print(f"\n   请安装缺失的包: pip install {' '.join(missing)}")
    
    # 检查配置
    print("\n3. 配置文件检查")
    if not check_config():
        all_ok = False
    
    # 检查目录
    print("\n4. 目录检查")
    check_directories()
    
    # 总结
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ 所有检查通过！可以运行程序了")
        print("\n运行命令: python -m app.main")
    else:
        print("❌ 部分检查未通过，请先解决上述问题")
    print("=" * 50)
    
    return all_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
