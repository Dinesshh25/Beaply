"""
scraping_sync.py
Modul untuk sync data beasiswa hasil scraping admin ke setiap user aplikasi.

Fitur:
  - Backup database admin sebelum sync
  - Prepare & package data untuk distribusi
  - Merge & update di user database dengan preservasi local data
  - Logging & tracking sync history
  - Conflict resolution untuk data duplikasi

Workflow Sync:
  1. Admin menjalankan scraping dan update data di database admin
  2. System membuat backup database admin (snapshot)
  3. System meng-export data beasiswa ke format distribusi (JSON)
  4. System create sync package dengan metadata & checksum
  5. Sync package didistribusikan ke setiap user aplikasi
  6. User aplikasi menerima & merge data dengan preservasi local changes
  7. Sync di-log untuk tracking & audit

Note:
  - User aplikasi TIDAK punya file scraping, hanya database & core files
  - Data bookmark user di-preserve saat update
  - Sync adalah one-way: admin → user (user tidak bisa push changes ke admin)
"""

import json
import logging
import os
import shutil
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ScrapingSyncManager:
    """Manager untuk sync beasiswa data dari admin ke user applications."""

    def __init__(
        self,
        admin_db_path: str,
        sync_output_dir: str = "./sync_packages",
        backup_dir: str = "./db_backups"
    ):
        """
        Initialize sync manager.

        Args:
            admin_db_path   : path ke admin beaply.db
            sync_output_dir : dir untuk output sync packages
            backup_dir      : dir untuk backup database admin
        """
        self.admin_db_path = admin_db_path
        self.sync_output_dir = Path(sync_output_dir)
        self.backup_dir = Path(backup_dir)

        # Create directories jika belum ada
        self.sync_output_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Buka koneksi ke admin database."""
        conn = sqlite3.connect(self.admin_db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def backup_admin_database(self, progress_callback=None) -> tuple[bool, str]:
        """
        Backup admin database sebelum sync (untuk disaster recovery).

        Returns:
            (sukses, backup_path_or_error_message)
        """
        try:
            if progress_callback:
                progress_callback("💾 Backup database admin...")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"beaply_backup_{timestamp}.db"

            shutil.copy2(self.admin_db_path, str(backup_path))

            if progress_callback:
                progress_callback(f"✓ Backup berhasil: {backup_path}")

            logger.info(f"Database backup created: {backup_path}")
            return True, str(backup_path)

        except Exception as e:
            logger.error(f"Error backup database: {e}")
            if progress_callback:
                progress_callback(f"⚠ Error backup: {e}")
            return False, str(e)

    def generate_sync_package(
        self,
        sumber_website: str = None,
        include_all: bool = True,
        progress_callback=None
    ) -> tuple[bool, str]:
        """
        Generate sync package berisi semua beasiswa data untuk distribusi ke user apps.

        Args:
            sumber_website  : jika spesifik, hanya sync beasiswa dari source ini
            include_all     : jika True, include semua sumber (jika sumber_website None)
            progress_callback: callback untuk progress reporting

        Returns:
            (sukses, path_package_atau_error)
        """
        try:
            if progress_callback:
                progress_callback("📦 Generate sync package...")

            # Ambil semua beasiswa dari database admin
            conn = self.get_connection()
            cur = conn.cursor()

            if sumber_website:
                cur.execute("SELECT * FROM beasiswa WHERE sumber_website = ? ORDER BY id", (sumber_website,))
            else:
                cur.execute("SELECT * FROM beasiswa ORDER BY id")

            rows = cur.fetchall()
            conn.close()

            if not rows:
                msg = f"Tidak ada data untuk sync {sumber_website if sumber_website else 'semua sumber'}"
                if progress_callback:
                    progress_callback(f"⚠ {msg}")
                return False, msg

            # Convert rows ke dict dan parse JSON fields
            data = []
            for row in rows:
                r = dict(row)

                # Parse JSON fields
                for field in ('jenjang', 'jurusan', 'kategori_raw'):
                    if r.get(field):
                        try:
                            r[field] = json.loads(r[field])
                        except (json.JSONDecodeError, TypeError):
                            pass

                # Parse data_json untuk full content
                if r.get('data_json'):
                    try:
                        r['data_json_parsed'] = json.loads(r['data_json'])
                    except (json.JSONDecodeError, TypeError):
                        pass

                data.append(r)

            # Create sync package metadata
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            package_id = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Generate checksum dari semua data untuk integrity check
            data_str = json.dumps(data, ensure_ascii=False, default=str, sort_keys=True)
            data_checksum = hashlib.sha256(data_str.encode('utf-8')).hexdigest()

            package_metadata = {
                'package_id': package_id,
                'timestamp': timestamp,
                'sumber_website': sumber_website or 'all',
                'total_beasiswa': len(data),
                'data_checksum': data_checksum,
                'format_version': '1.0',
                'description': f"Sync package berisi {len(data)} beasiswa dari {sumber_website or 'semua sumber'}"
            }

            # Create package dict
            package = {
                'metadata': package_metadata,
                'data': data
            }

            # Save package ke file JSON
            package_filename = f"sync_package_{package_id}.json"
            package_path = self.sync_output_dir / package_filename

            with open(package_path, 'w', encoding='utf-8') as f:
                json.dump(package, f, ensure_ascii=False, indent=2, default=str)

            if progress_callback:
                progress_callback(f"✓ Package berhasil di-generate: {package_path}")
                progress_callback(f"  Package ID: {package_id}")
                progress_callback(f"  Total beasiswa: {len(data)}")
                progress_callback(f"  Checksum: {data_checksum}")

            logger.info(f"Sync package generated: {package_path} ({len(data)} beasiswa)")

            return True, str(package_path)

        except Exception as e:
            logger.error(f"Error generate sync package: {e}")
            if progress_callback:
                progress_callback(f"⚠ Error generate package: {e}")
            return False, str(e)

    def create_sync_manifest(
        self,
        package_path: str,
        sync_destinations: list[str] = None,
        progress_callback=None
    ) -> tuple[bool, str]:
        """
        Create manifest file untuk track sync destinations & status.

        Args:
            package_path        : path ke sync package
            sync_destinations   : list of user aplikasi paths (opsional)

        Returns:
            (sukses, manifest_path)
        """
        try:
            if progress_callback:
                progress_callback("📋 Create sync manifest...")

            # Read package untuk extract metadata
            with open(package_path, 'r', encoding='utf-8') as f:
                package = json.load(f)

            package_id = package['metadata']['package_id']
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create manifest
            manifest = {
                'manifest_version': '1.0',
                'created_at': timestamp,
                'package_id': package_id,
                'package_path': str(package_path),
                'package_metadata': package['metadata'],
                'sync_destinations': sync_destinations or [],
                'sync_status': {
                    'total_destinations': len(sync_destinations) if sync_destinations else 0,
                    'synced': 0,
                    'pending': len(sync_destinations) if sync_destinations else 0,
                    'failed': 0,
                },
                'sync_history': []
            }

            # Save manifest
            manifest_filename = f"manifest_{package_id}.json"
            manifest_path = self.sync_output_dir / manifest_filename

            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2, default=str)

            if progress_callback:
                progress_callback(f"✓ Manifest created: {manifest_path}")

            logger.info(f"Sync manifest created: {manifest_path}")

            return True, str(manifest_path)

        except Exception as e:
            logger.error(f"Error create manifest: {e}")
            if progress_callback:
                progress_callback(f"⚠ Error create manifest: {e}")
            return False, str(e)

    def verify_sync_package_integrity(self, package_path: str, progress_callback=None) -> tuple[bool, str]:
        """
        Verify integrity sync package menggunakan checksum.

        Args:
            package_path: path ke sync package JSON

        Returns:
            (valid, message)
        """
        try:
            if progress_callback:
                progress_callback("🔍 Verify package integrity...")

            with open(package_path, 'r', encoding='utf-8') as f:
                package = json.load(f)

            # Extract stored checksum
            stored_checksum = package['metadata'].get('data_checksum')
            if not stored_checksum:
                return False, "Checksum tidak ditemukan di package"

            # Regenerate checksum dari data
            data = package['data']
            data_str = json.dumps(data, ensure_ascii=False, default=str, sort_keys=True)
            computed_checksum = hashlib.sha256(data_str.encode('utf-8')).hexdigest()

            # Bandingkan
            if stored_checksum == computed_checksum:
                if progress_callback:
                    progress_callback(f"✓ Package integrity verified: {computed_checksum}")
                return True, "Package valid"
            else:
                msg = f"Checksum mismatch! Stored: {stored_checksum}, Computed: {computed_checksum}"
                if progress_callback:
                    progress_callback(f"⚠ {msg}")
                return False, msg

        except Exception as e:
            logger.error(f"Error verify package: {e}")
            if progress_callback:
                progress_callback(f"⚠ Error verify: {e}")
            return False, str(e)

    def record_sync_event(
        self,
        package_id: str,
        destination: str,
        event_type: str,  # 'SYNC_STARTED', 'SYNC_SUCCESS', 'SYNC_FAILED', 'SYNC_VERIFIED'
        status: str = 'SUCCESS',  # 'SUCCESS', 'ERROR', 'WARNING'
        details: str = None
    ) -> bool:
        """
        Record sync event untuk tracking & analytics.

        Args:
            package_id  : ID dari sync package
            destination : user aplikasi destination path/identifier
            event_type  : tipe event
            status      : status event
            details     : detail message

        Returns:
            True jika berhasil di-record
        """
        try:
            sync_log_dir = self.sync_output_dir / "sync_logs"
            sync_log_dir.mkdir(exist_ok=True)

            # Use manifest untuk store sync history
            manifest_path = self.sync_output_dir / f"manifest_{package_id}.json"
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)

                # Add event ke history
                event = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'destination': destination,
                    'event_type': event_type,
                    'status': status,
                    'details': details
                }
                manifest['sync_history'].append(event)

                # Update status
                if event_type == 'SYNC_SUCCESS':
                    manifest['sync_status']['synced'] += 1
                    manifest['sync_status']['pending'] -= 1
                elif event_type == 'SYNC_FAILED':
                    manifest['sync_status']['failed'] += 1
                    manifest['sync_status']['pending'] -= 1

                # Save updated manifest
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest, f, ensure_ascii=False, indent=2, default=str)

                logger.info(f"Sync event recorded: {package_id} -> {destination}: {event_type}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error record sync event: {e}")
            return False

    def get_sync_statistics(self, progress_callback=None) -> dict:
        """
        Get statistik lengkap dari semua sync operations.

        Returns:
            dict dengan sync statistics
        """
        try:
            if progress_callback:
                progress_callback("📊 Generate sync statistics...")

            # Count packages
            packages = list(self.sync_output_dir.glob("sync_package_*.json"))
            manifests = list(self.sync_output_dir.glob("manifest_*.json"))

            total_synced = 0
            total_failed = 0
            latest_package = None

            # Parse manifests untuk stats
            for manifest_file in sorted(manifests, reverse=True):
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)

                    if not latest_package:
                        latest_package = manifest

                    total_synced += manifest['sync_status'].get('synced', 0)
                    total_failed += manifest['sync_status'].get('failed', 0)

            stats = {
                'total_packages': len(packages),
                'total_manifests': len(manifests),
                'total_synced': total_synced,
                'total_failed': total_failed,
                'latest_package': latest_package,
                'sync_dir': str(self.sync_output_dir),
                'backup_dir': str(self.backup_dir),
            }

            if progress_callback:
                progress_callback(f"✓ Sync stats: {len(packages)} packages, {total_synced} synced, {total_failed} failed")

            return stats

        except Exception as e:
            logger.error(f"Error get sync statistics: {e}")
            if progress_callback:
                progress_callback(f"⚠ Error get stats: {e}")
            return {}


# ─── Convenience Functions ────────────────────────────────────────────────────

def setup_sync_manager(
    admin_db_path: str,
    sync_output_dir: str = None,
    backup_dir: str = None
) -> ScrapingSyncManager:
    """
    Setup ScrapingSyncManager dengan default paths.

    Args:
        admin_db_path   : path ke admin beaply.db
        sync_output_dir : custom output dir (default: ./sync_packages)
        backup_dir      : custom backup dir (default: ./db_backups)

    Returns:
        ScrapingSyncManager instance
    """
    if not sync_output_dir:
        sync_output_dir = os.path.join(
            os.path.dirname(admin_db_path),
            "sync_packages"
        )

    if not backup_dir:
        backup_dir = os.path.join(
            os.path.dirname(admin_db_path),
            "db_backups"
        )

    return ScrapingSyncManager(
        admin_db_path=admin_db_path,
        sync_output_dir=sync_output_dir,
        backup_dir=backup_dir
    )


if __name__ == '__main__':
    # Simple test
    print("=== Test scraping_sync.py ===\n")

    # Setup manager
    db_path = r"c:\PROYEK1\Beaply\beaply.db"
    if os.path.exists(db_path):
        manager = setup_sync_manager(db_path)

        # Run sync operations
        print("[1] Backup admin database...")
        ok, msg = manager.backup_admin_database(lambda m: print(f"  {m}"))
        print(f"  Result: {'OK' if ok else 'FAIL'} - {msg}\n")

        print("[2] Generate sync package...")
        ok, msg = manager.generate_sync_package(progress_callback=lambda m: print(f"  {m}"))
        print(f"  Result: {'OK' if ok else 'FAIL'} - {msg}\n")

        if ok:
            print("[3] Verify package integrity...")
            ok, msg = manager.verify_sync_package_integrity(msg, lambda m: print(f"  {m}"))
            print(f"  Result: {'OK' if ok else 'FAIL'} - {msg}\n")

        print("[4] Get sync statistics...")
        stats = manager.get_sync_statistics(lambda m: print(f"  {m}"))
        print(f"  Stats: {stats}\n")
    else:
        print(f"Database tidak ditemukan: {db_path}")
