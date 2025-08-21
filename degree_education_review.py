#!/usr/bin/env python3
"""
《学位与研究生教育》期刊专用AI审稿示例脚本

此脚本演示如何使用定制的配置文件对投稿论文进行专业审稿。
"""

import sys
from pathlib import Path
from ai_peer_review.review import process_paper, generate_meta_review, save_concerns_as_csv


def review_paper_for_degree_education_journal(pdf_path: str, output_dir: str = "review_output"):
    """
    使用《学位与研究生教育》期刊定制配置审稿论文
    
    Args:
        pdf_path: 待审稿论文的PDF路径
        output_dir: 审稿结果输出目录
    """
    # 配置文件路径
    config_file = "configs/degree_education_journal.json"
    
    # 建议的模型组合（可根据实际情况调整）
    models = [
        "gpt-4o",           # OpenAI GPT-4
        "claude-3-sonnet",  # Anthropic Claude
        "deepseek-chat",    # DeepSeek
        "gemini-pro"        # Google Gemini
    ]
    
    print(f"开始审稿论文: {pdf_path}")
    print(f"使用配置: {config_file}")
    print(f"使用模型: {', '.join(models)}")
    print("-" * 50)
    
    try:
        # 第一步：生成各模型的独立评审
        print("正在生成独立评审报告...")
        reviews = process_paper(
            pdf_path=pdf_path,
            models=models,
            config_file=config_file
        )
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 保存各模型的独立评审
        for model_name, review_text in reviews.items():
            review_file = output_path / f"review_{model_name.replace(':', '_')}.txt"
            with open(review_file, "w", encoding="utf-8") as f:
                f.write(f"《学位与研究生教育》期刊审稿报告\n")
                f.write(f"审稿模型: {model_name}\n")
                f.write(f"论文文件: {pdf_path}\n")
                f.write("=" * 60 + "\n\n")
                f.write(review_text)
            print(f"已保存 {model_name} 的评审报告: {review_file}")
        
        # 第二步：生成元评审报告
        print("\n正在生成元评审报告...")
        meta_review_text, nato_to_model = generate_meta_review(
            reviews=reviews,
            config_file=config_file
        )
        
        # 保存元评审报告
        meta_review_file = output_path / "meta_review.txt"
        with open(meta_review_file, "w", encoding="utf-8") as f:
            f.write(f"《学位与研究生教育》期刊元评审报告\n")
            f.write(f"论文文件: {pdf_path}\n")
            f.write("=" * 60 + "\n\n")
            f.write("评审专家代码映射:\n")
            for nato_name, model_name in nato_to_model.items():
                f.write(f"  {nato_name} -> {model_name}\n")
            f.write("\n" + "=" * 60 + "\n\n")
            f.write(meta_review_text)
        print(f"已保存元评审报告: {meta_review_file}")
        
        # 第三步：生成关注问题汇总表
        print("\n正在生成关注问题汇总表...")
        concerns_saved = save_concerns_as_csv(meta_review_text, output_path)
        if concerns_saved:
            print(f"已保存关注问题汇总表: {output_path / 'concerns_table.csv'}")
        
        # 生成审稿总结
        summary_file = output_path / "review_summary.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"《学位与研究生教育》期刊AI审稿总结\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"论文文件: {pdf_path}\n")
            f.write(f"审稿日期: {Path(pdf_path).stat().st_mtime}\n")
            f.write(f"参与模型: {len(models)}个\n")
            f.write(f"配置文件: {config_file}\n\n")
            f.write("生成文件列表:\n")
            for model_name in models:
                f.write(f"  - review_{model_name.replace(':', '_')}.txt (独立评审)\n")
            f.write(f"  - meta_review.txt (元评审报告)\n")
            if concerns_saved:
                f.write(f"  - concerns_table.csv (关注问题汇总)\n")
            f.write(f"  - review_summary.txt (本总结文件)\n\n")
            f.write("审稿标准:\n")
            f.write("  ✓ 选题价值与期刊契合度\n")
            f.write("  ✓ 学术质量与创新性\n")
            f.write("  ✓ 学术规范性\n")
            f.write("  ✓ 写作质量与规范\n")
            f.write("  ✓ 研究方法与论证\n")
        
        print(f"\n审稿完成！所有文件已保存到: {output_path}")
        print(f"审稿总结文件: {summary_file}")
        
    except Exception as e:
        print(f"审稿过程中出现错误: {e}")
        sys.exit(1)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print(f"  python {sys.argv[0]} <PDF文件路径> [输出目录]")
        print("\n示例:")
        print(f"  python {sys.argv[0]} paper.pdf")
        print(f"  python {sys.argv[0]} paper.pdf my_review_output")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "review_output"
    
    # 检查PDF文件是否存在
    if not Path(pdf_path).exists():
        print(f"错误: 找不到文件 {pdf_path}")
        sys.exit(1)
    
    # 开始审稿
    review_paper_for_degree_education_journal(pdf_path, output_dir)


if __name__ == "__main__":
    main()
