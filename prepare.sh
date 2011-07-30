#!/bin/sh

MASTER=master
FRONTEND=frontend
USERNAME=friend

MASTER_BACKUP="$MASTER.dump"
FRONTEND_BACKUP="$FRONTEND.dump"

IDENTS_CLUSTER_IDX=idents_title_index
FRIENDS_CLUSTER_INDEX=friends_cluster_index
WEB_CLUSTER_INDEX=web_cluster_index

psql -U $USERNAME $FRONTEND -c "TRUNCATE idents CASCADE"
psql -U $USERNAME $FRONTEND -c "TRUNCATE urls CASCADE"

PYTHONPATH=.:./littlebrother python littlebrother/db/prepare.py

psql -U $USERNAME $FRONTEND -c "DROP INDEX IF EXISTS $IDENTS_CLUSTER_IDX"
psql -U $USERNAME $FRONTEND -c "CREATE INDEX $IDENTS_CLUSTER_IDX ON idents (title varchar_pattern_ops, score DESC)"

psql -U $USERNAME $FRONTEND -c "CLUSTER $IDENTS_CLUSTER_IDX ON idents"
psql -U $USERNAME $FRONTEND -c "ANALYZE idents"

###

psql -U $USERNAME $FRONTEND -c "DROP INDEX IF EXISTS $FRIENDS_CLUSTER_INDEX"
psql -U $USERNAME $FRONTEND -c "CREATE INDEX $FRIENDS_CLUSTER_INDEX ON friends (ident_1_id, score DESC, ident_2_tag, ident_2_title varchar_pattern_ops)"

psql -U $USERNAME $FRONTEND -c "CLUSTER $FRIENDS_CLUSTER_INDEX ON friends"
psql -U $USERNAME $FRONTEND -c "ANALYZE friends"

###

psql -U $USERNAME $FRONTEND -c "DROP INDEX IF EXISTS $WEB_CLUSTER_INDEX"
psql -U $USERNAME $FRONTEND -c "CREATE INDEX $WEB_CLUSTER_INDEX ON web (ident_id, url_title varchar_pattern_ops, url_ref varchar_pattern_ops)"

psql -U $USERNAME $FRONTEND -c "CLUSTER $WEB_CLUSTER_INDEX ON web"
psql -U $USERNAME $FRONTEND -c "ANALYZE web"

###

pg_dump -U friend $MASTER > $MASTER_BACKUP
gzip -f $MASTER_BACKUP

pg_dump -U friend $FRONTEND > $FRONTEND_BACKUP
gzip -f $FRONTEND_BACKUP
