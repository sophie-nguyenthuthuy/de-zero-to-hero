#!/usr/bin/env python3
"""
ETL Pipeline CLI — Data Engineer Lab B02

Sử dụng:
    python src/etl_pipeline.py --input data/raw/orders.csv --output-dir data/processed --format parquet
    python src/etl_pipeline.py --input data/raw/orders.csv --partition-by status
    python src/etl_pipeline.py --help
"""
import argparse
import logging
import sys
import time
from pathlib import Path

# Setup logging sớm
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="etl_pipeline",
        description="🔄 ETL Pipeline — Extract, Transform, Load data files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  # Cơ bản
  python src/etl_pipeline.py --input data/raw/orders.csv
  # Chỉ định output format
  python src/etl_pipeline.py --input data/raw/orders.csv --format json
  # Partition theo cột status
  python src/etl_pipeline.py --input data/raw/orders.csv --partition-by status
  # Verbose mode
  python src/etl_pipeline.py --input data/raw/orders.csv --verbose
        """,
    )

    # Input
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Đường dẫn file input (CSV, JSON, Parquet, JSONL)",
    )

    # Output
    parser.add_argument(
        "--output-dir", "-o",
        default="data/processed",
        help="Thư mục output (default: data/processed)",
    )
    parser.add_argument(
        "--output-name",
        default=None,
        help="Tên file output (default: tên file input + _clean)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["csv", "json", "parquet", "jsonl"],
        default="parquet",
        help="Format output (default: parquet)",
    )

    # Options
    parser.add_argument(
        "--partition-by",
        default=None,
        help="Partition output theo column (ví dụ: status, date)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Tạo báo cáo JSON sau khi chạy",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chạy thử không ghi file",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Import ở đây để tránh circular import
    from extractors.file_extractor import FileExtractor
    from loaders.file_loader import FileLoader
    from transformers.order_transformer import OrderTransformer

    start_time = time.time()

    logger.info("=" * 50)
    logger.info("  ETL PIPELINE START")
    logger.info(f"  Input  : {args.input}")
    logger.info(f"  Output : {args.output_dir}")
    logger.info(f"  Format : {args.format}")
    logger.info("=" * 50)

    try:
        # ===== EXTRACT =====
        logger.info("\n[1/3] EXTRACT")
        extractor = FileExtractor()
        df_raw = extractor.extract(args.input)
        logger.info(f"Extracted: {len(df_raw):,} rows")

        # ===== TRANSFORM =====
        logger.info("\n[2/3] TRANSFORM")
        transformer = OrderTransformer()
        df_clean = transformer.transform(df_raw)
        logger.info(f"Transformed: {len(df_clean):,} rows")

        if args.dry_run:
            logger.info("\n[DRY RUN] Không ghi file. Kết quả preview:")
            print(df_clean.head())
            return 0

        # ===== LOAD =====
        logger.info("\n[3/3] LOAD")
        loader = FileLoader(base_dir=args.output_dir)

        output_name = args.output_name or (Path(args.input).stem + "_clean")

        output_files = loader.load(
            df_clean,
            filename=output_name,
            format=args.format,
            partition_by=args.partition_by,
        )

        # Report
        if args.report:
            report_path = f"{args.output_dir}/{output_name}_report.json"
            loader.generate_report(df_clean, report_path)

        elapsed = time.time() - start_time
        logger.info("\n" + "=" * 50)
        logger.info("  ETL PIPELINE COMPLETE")
        logger.info(f"  Input rows : {len(df_raw):,}")
        logger.info(f"  Output rows: {len(df_clean):,}")
        logger.info(f"  Files      : {len(output_files)}")
        logger.info(f"  Time       : {elapsed:.2f}s")
        logger.info("=" * 50)

        return 0

    except FileNotFoundError as e:
        logger.error(f"File không tìm thấy: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Pipeline thất bại: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
