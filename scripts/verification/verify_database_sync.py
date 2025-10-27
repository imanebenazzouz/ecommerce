#!/usr/bin/env python3
"""
Script de vérification de la synchronisation entre les modèles et la base de données
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from datetime import datetime

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce:ecommerce123@127.0.0.1:5432/ecommerce")

def check_table_exists(cursor, table_name):
    """Vérifie si une table existe"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        )
    """, (table_name,))
    return cursor.fetchone()[0]

def get_table_columns(cursor, table_name):
    """Récupère les colonnes d'une table"""
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    return cursor.fetchall()

def verify_database_structure():
    """Vérifie la structure complète de la base de données"""
    
    print("=" * 80)
    print("🔍 VÉRIFICATION DE LA SYNCHRONISATION BASE DE DONNÉES")
    print("=" * 80)
    print(f"⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Base de données: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Non définie'}")
    print("=" * 80)
    print()
    
    # Tables attendues
    expected_tables = [
        'users',
        'products',
        'carts',
        'cart_items',
        'orders',
        'order_items',
        'deliveries',
        'invoices',
        'payments',
        'message_threads',
        'messages'
    ]
    
    # Colonnes attendues pour la table payments (modifications récentes)
    expected_payment_columns = {
        'id': 'uuid',
        'order_id': 'uuid',
        'amount_cents': 'integer',
        'status': 'character varying',
        'payment_method': 'character varying',
        'created_at': 'timestamp without time zone',
        'card_last4': 'character varying',  # Nouveau champ
        'postal_code': 'character varying',  # Nouveau champ
        'phone': 'character varying',  # Nouveau champ
        'street_number': 'character varying',  # Nouveau champ
        'street_name': 'character varying',  # Nouveau champ
    }
    
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ Connexion à la base de données réussie")
        print()
        
        # Vérifier l'existence des tables
        print("📋 VÉRIFICATION DES TABLES")
        print("-" * 80)
        all_tables_exist = True
        for table in expected_tables:
            exists = check_table_exists(cursor, table)
            status = "✅" if exists else "❌"
            print(f"{status} Table '{table}': {'Existe' if exists else 'MANQUANTE'}")
            if not exists:
                all_tables_exist = False
        print()
        
        if not all_tables_exist:
            print("⚠️  ATTENTION: Des tables sont manquantes!")
            print("   Exécutez les migrations ou initialisez la base de données.")
            print()
        
        # Vérifier la structure de la table payments (modifications récentes)
        print("💳 VÉRIFICATION DÉTAILLÉE DE LA TABLE PAYMENTS")
        print("-" * 80)
        
        if check_table_exists(cursor, 'payments'):
            columns = get_table_columns(cursor, 'payments')
            actual_columns = {col[0]: col[1] for col in columns}
            
            print("Colonnes attendues vs. colonnes présentes:")
            print()
            
            all_columns_present = True
            for col_name, col_type in expected_payment_columns.items():
                if col_name in actual_columns:
                    type_match = col_type in actual_columns[col_name] or actual_columns[col_name] in col_type
                    status = "✅" if type_match else "⚠️"
                    type_info = f"(Type: {actual_columns[col_name]})"
                    print(f"{status} {col_name:20} {type_info}")
                else:
                    print(f"❌ {col_name:20} MANQUANTE")
                    all_columns_present = False
            
            print()
            
            # Vérifier les colonnes supplémentaires non attendues
            extra_columns = set(actual_columns.keys()) - set(expected_payment_columns.keys())
            if extra_columns:
                print(f"ℹ️  Colonnes supplémentaires trouvées: {', '.join(extra_columns)}")
                print()
            
            if all_columns_present:
                print("✅ Tous les champs de paiement sont présents et synchronisés!")
            else:
                print("❌ Des champs de paiement sont manquants!")
                print("   Exécutez les scripts de migration:")
                print("   - python ecommerce-backend/migrate_payment_fields.py")
                print("   - python ecommerce-backend/migrate_add_street_name.py")
            print()
        else:
            print("❌ La table payments n'existe pas!")
            print()
        
        # Vérifier les données
        print("📊 STATISTIQUES DES DONNÉES")
        print("-" * 80)
        
        for table in expected_tables:
            if check_table_exists(cursor, table):
                cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
                count = cursor.fetchone()[0]
                print(f"  {table:20} : {count:5} enregistrements")
        print()
        
        # Vérifier l'intégrité des contraintes de clés étrangères
        print("🔗 VÉRIFICATION DES CONTRAINTES D'INTÉGRITÉ")
        print("-" * 80)
        
        cursor.execute("""
            SELECT
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name
        """)
        
        fk_constraints = cursor.fetchall()
        print(f"✅ {len(fk_constraints)} contraintes de clés étrangères définies")
        print()
        
        # Vérifier les index
        print("📑 VÉRIFICATION DES INDEX")
        print("-" * 80)
        
        cursor.execute("""
            SELECT 
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        
        indexes = cursor.fetchall()
        index_count_by_table = {}
        for idx in indexes:
            table = idx[0]
            index_count_by_table[table] = index_count_by_table.get(table, 0) + 1
        
        for table, count in sorted(index_count_by_table.items()):
            print(f"  {table:20} : {count:2} index")
        print()
        
        # Résumé final
        print("=" * 80)
        print("📝 RÉSUMÉ DE LA VÉRIFICATION")
        print("=" * 80)
        
        if all_tables_exist and all_columns_present:
            print("✅ ✅ ✅  TOUT EST SYNCHRONISÉ ET À JOUR! ✅ ✅ ✅")
            print()
            print("Votre base de données est complètement synchronisée avec vos modèles.")
            print("Tous les champs de paiement récemment ajoutés sont présents.")
            return_code = 0
        else:
            print("⚠️  ⚠️  ⚠️   DES ACTIONS SONT NÉCESSAIRES  ⚠️  ⚠️  ⚠️")
            print()
            if not all_tables_exist:
                print("❌ Des tables sont manquantes - Exécutez: python ecommerce-backend/init_db.py")
            if not all_columns_present:
                print("❌ Des colonnes sont manquantes - Exécutez les migrations:")
                print("   cd ecommerce-backend")
                print("   python migrate_payment_fields.py")
                print("   python migrate_add_street_name.py")
            return_code = 1
        
        print("=" * 80)
        print()
        
        cursor.close()
        conn.close()
        
        return return_code
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        print()
        print("Vérifiez que:")
        print("  1. PostgreSQL est démarré")
        print("  2. La base de données 'ecommerce' existe")
        print("  3. Les credentials sont corrects")
        print("  4. La variable DATABASE_URL est correctement définie")
        return 1
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(verify_database_structure())

