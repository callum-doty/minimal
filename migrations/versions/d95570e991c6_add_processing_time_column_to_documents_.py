"""Add processing_time column to documents table

Revision ID: d95570e991c6
Revises: add_display_order
Create Date: 2025-05-06 22:33:10.871358

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd95570e991c6'
down_revision = 'add_display_order'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('batch_jobs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('job_name', sa.Text(), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('file_size', sa.BigInteger(), nullable=False),
    sa.Column('status', sa.Text(), nullable=False),
    sa.Column('total_documents', sa.Integer(), nullable=False),
    sa.Column('processed_documents', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_name', sa.Text(), nullable=True),
    sa.Column('campaign_name', sa.Text(), nullable=True),
    sa.Column('created_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('document_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dropbox_syncs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=True),
    sa.Column('dropbox_file_id', sa.String(length=255), nullable=True),
    sa.Column('dropbox_path', sa.String(length=512), nullable=True),
    sa.Column('sync_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('dropbox_file_id')
    )
    op.create_table('search_feedback',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('search_query', sa.Text(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=True),
    sa.Column('feedback_type', sa.String(length=50), nullable=True),
    sa.Column('feedback_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('user_comment', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('classifications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confidence', sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column('classification_date', sa.DateTime(timezone=True), nullable=True))
        batch_op.alter_column('category',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.drop_index('ix_classifications_category')
        batch_op.drop_index('ix_classifications_document_id')

    with op.batch_alter_table('communication_focus', schema=None) as batch_op:
        batch_op.add_column(sa.Column('secondary_issues', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('messaging_strategy', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('created_date', sa.DateTime(timezone=True), nullable=True))
        batch_op.alter_column('primary_issue',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.drop_index('ix_communication_focus_document_id')
        batch_op.drop_index('ix_communication_focus_primary_issue')

    with op.batch_alter_table('design_elements', schema=None) as batch_op:
        batch_op.add_column(sa.Column('color_scheme', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('theme', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('mail_piece_type', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('target_audience', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('campaign_name', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('visual_elements', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('confidence', sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column('created_date', sa.DateTime(timezone=True), nullable=True))
        batch_op.alter_column('geographic_location',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.drop_index('ix_design_elements_document_id')
        batch_op.drop_index('ix_design_elements_geographic_location')

    with op.batch_alter_table('document_keywords', schema=None) as batch_op:
        batch_op.add_column(sa.Column('relevance_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('extraction_date', sa.DateTime(timezone=True), nullable=True))
        batch_op.alter_column('display_order',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
        batch_op.drop_index('ix_document_keywords_display_order')
        batch_op.drop_index('ix_document_keywords_document_id')
        batch_op.drop_index('ix_document_keywords_taxonomy_id')

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('processing_time', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('file_size', sa.BigInteger(), nullable=False))
        batch_op.add_column(sa.Column('page_count', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('batch_jobs_id', sa.Integer(), nullable=True))
        batch_op.alter_column('filename',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               nullable=False)
        batch_op.alter_column('upload_date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               nullable=False)
        batch_op.drop_index('ix_documents_embeddings', postgresql_using='gin')
        batch_op.drop_index('ix_documents_filename')
        batch_op.drop_index('ix_documents_search_vector', postgresql_using='gin')
        batch_op.drop_index('ix_documents_status')
        batch_op.drop_index('ix_documents_upload_date')
        batch_op.create_foreign_key(None, 'batch_jobs', ['batch_jobs_id'], ['id'])
        batch_op.drop_column('embeddings')

    with op.batch_alter_table('entities', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creation_date', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('survey_question', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('file_identifier', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('created_date', sa.DateTime(timezone=True), nullable=True))
        batch_op.alter_column('client_name',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.alter_column('opponent_name',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.drop_index('ix_entities_client_name')
        batch_op.drop_index('ix_entities_document_id')
        batch_op.drop_index('ix_entities_opponent_name')

    with op.batch_alter_table('extracted_text', schema=None) as batch_op:
        batch_op.add_column(sa.Column('page_number', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('text_content', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('call_to_action', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('candidate_name', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('opponent_name', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('confidence', sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column('extraction_date', sa.DateTime(timezone=True), nullable=True))
        batch_op.alter_column('main_message',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.alter_column('supporting_text',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.drop_index('ix_extracted_text_document_id')
        batch_op.drop_index('ix_extracted_text_main_message')
        batch_op.drop_index('ix_extracted_text_search_vector', postgresql_using='gin')
        batch_op.drop_index('ix_extracted_text_supporting_text')
        batch_op.drop_column('search_vector')

    with op.batch_alter_table('keyword_synonyms', schema=None) as batch_op:
        batch_op.alter_column('synonym',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               nullable=False)
        batch_op.drop_index('ix_keyword_synonyms_synonym')
        batch_op.drop_index('ix_keyword_synonyms_taxonomy_id')

    with op.batch_alter_table('keyword_taxonomy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('specific_term', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('created_date', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('parent_id', sa.Integer(), nullable=True))
        batch_op.alter_column('term',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               nullable=False)
        batch_op.alter_column('primary_category',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               nullable=False)
        batch_op.alter_column('subcategory',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.drop_index('ix_keyword_taxonomy_primary_category')
        batch_op.drop_index('ix_keyword_taxonomy_subcategory')
        batch_op.drop_index('ix_keyword_taxonomy_term')
        batch_op.create_foreign_key(None, 'keyword_taxonomy', ['parent_id'], ['id'])

    with op.batch_alter_table('llm_analysis', schema=None) as batch_op:
        batch_op.add_column(sa.Column('visual_analysis', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('content_analysis', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('confidence_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('analysis_date', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('model_version', sa.Text(), nullable=True))
        batch_op.alter_column('summary_description',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.alter_column('campaign_type',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.alter_column('election_year',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.alter_column('document_tone',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.drop_index('ix_llm_analysis_campaign_type')
        batch_op.drop_index('ix_llm_analysis_document_id')
        batch_op.drop_index('ix_llm_analysis_document_tone')
        batch_op.drop_index('ix_llm_analysis_election_year')
        batch_op.drop_index('ix_llm_analysis_embeddings', postgresql_using='gin')
        batch_op.drop_index('ix_llm_analysis_search_vector', postgresql_using='gin')
        batch_op.drop_index('ix_llm_analysis_summary')
        batch_op.drop_column('search_vector')
        batch_op.drop_column('embeddings')

    with op.batch_alter_table('llm_keywords', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('relevance_score', sa.BigInteger(), nullable=True))
        batch_op.alter_column('keyword',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.drop_index('ix_llm_keywords_analysis_id')
        batch_op.drop_index('ix_llm_keywords_keyword')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('llm_keywords', schema=None) as batch_op:
        batch_op.create_index('ix_llm_keywords_keyword', ['keyword'], unique=False)
        batch_op.create_index('ix_llm_keywords_analysis_id', ['llm_analysis_id'], unique=False)
        batch_op.alter_column('keyword',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.drop_column('relevance_score')
        batch_op.drop_column('category')

    with op.batch_alter_table('llm_analysis', schema=None) as batch_op:
        batch_op.add_column(sa.Column('embeddings', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('search_vector', postgresql.TSVECTOR(), autoincrement=False, nullable=True))
        batch_op.create_index('ix_llm_analysis_summary', ['summary_description'], unique=False)
        batch_op.create_index('ix_llm_analysis_search_vector', ['search_vector'], unique=False, postgresql_using='gin')
        batch_op.create_index('ix_llm_analysis_embeddings', ['embeddings'], unique=False, postgresql_using='gin')
        batch_op.create_index('ix_llm_analysis_election_year', ['election_year'], unique=False)
        batch_op.create_index('ix_llm_analysis_document_tone', ['document_tone'], unique=False)
        batch_op.create_index('ix_llm_analysis_document_id', ['document_id'], unique=False)
        batch_op.create_index('ix_llm_analysis_campaign_type', ['campaign_type'], unique=False)
        batch_op.alter_column('document_tone',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('election_year',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('campaign_type',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('summary_description',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.drop_column('model_version')
        batch_op.drop_column('analysis_date')
        batch_op.drop_column('confidence_score')
        batch_op.drop_column('content_analysis')
        batch_op.drop_column('visual_analysis')

    with op.batch_alter_table('keyword_taxonomy', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_index('ix_keyword_taxonomy_term', ['term'], unique=False)
        batch_op.create_index('ix_keyword_taxonomy_subcategory', ['subcategory'], unique=False)
        batch_op.create_index('ix_keyword_taxonomy_primary_category', ['primary_category'], unique=False)
        batch_op.alter_column('subcategory',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('primary_category',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('term',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               nullable=True)
        batch_op.drop_column('parent_id')
        batch_op.drop_column('created_date')
        batch_op.drop_column('description')
        batch_op.drop_column('specific_term')

    with op.batch_alter_table('keyword_synonyms', schema=None) as batch_op:
        batch_op.create_index('ix_keyword_synonyms_taxonomy_id', ['taxonomy_id'], unique=False)
        batch_op.create_index('ix_keyword_synonyms_synonym', ['synonym'], unique=False)
        batch_op.alter_column('synonym',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               nullable=True)

    with op.batch_alter_table('extracted_text', schema=None) as batch_op:
        batch_op.add_column(sa.Column('search_vector', postgresql.TSVECTOR(), autoincrement=False, nullable=True))
        batch_op.create_index('ix_extracted_text_supporting_text', ['supporting_text'], unique=False)
        batch_op.create_index('ix_extracted_text_search_vector', ['search_vector'], unique=False, postgresql_using='gin')
        batch_op.create_index('ix_extracted_text_main_message', ['main_message'], unique=False)
        batch_op.create_index('ix_extracted_text_document_id', ['document_id'], unique=False)
        batch_op.alter_column('supporting_text',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('main_message',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.drop_column('extraction_date')
        batch_op.drop_column('confidence')
        batch_op.drop_column('opponent_name')
        batch_op.drop_column('candidate_name')
        batch_op.drop_column('call_to_action')
        batch_op.drop_column('text_content')
        batch_op.drop_column('page_number')

    with op.batch_alter_table('entities', schema=None) as batch_op:
        batch_op.create_index('ix_entities_opponent_name', ['opponent_name'], unique=False)
        batch_op.create_index('ix_entities_document_id', ['document_id'], unique=False)
        batch_op.create_index('ix_entities_client_name', ['client_name'], unique=False)
        batch_op.alter_column('opponent_name',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('client_name',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.drop_column('created_date')
        batch_op.drop_column('file_identifier')
        batch_op.drop_column('survey_question')
        batch_op.drop_column('creation_date')

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('embeddings', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_index('ix_documents_upload_date', ['upload_date'], unique=False)
        batch_op.create_index('ix_documents_status', ['status'], unique=False)
        batch_op.create_index('ix_documents_search_vector', ['search_vector'], unique=False, postgresql_using='gin')
        batch_op.create_index('ix_documents_filename', ['filename'], unique=False)
        batch_op.create_index('ix_documents_embeddings', ['embeddings'], unique=False, postgresql_using='gin')
        batch_op.alter_column('status',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('upload_date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
        batch_op.alter_column('filename',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               nullable=True)
        batch_op.drop_column('batch_jobs_id')
        batch_op.drop_column('page_count')
        batch_op.drop_column('file_size')
        batch_op.drop_column('processing_time')

    with op.batch_alter_table('document_keywords', schema=None) as batch_op:
        batch_op.create_index('ix_document_keywords_taxonomy_id', ['taxonomy_id'], unique=False)
        batch_op.create_index('ix_document_keywords_document_id', ['document_id'], unique=False)
        batch_op.create_index('ix_document_keywords_display_order', ['display_order'], unique=False)
        batch_op.alter_column('display_order',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('0'))
        batch_op.drop_column('extraction_date')
        batch_op.drop_column('relevance_score')

    with op.batch_alter_table('design_elements', schema=None) as batch_op:
        batch_op.create_index('ix_design_elements_geographic_location', ['geographic_location'], unique=False)
        batch_op.create_index('ix_design_elements_document_id', ['document_id'], unique=False)
        batch_op.alter_column('geographic_location',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.drop_column('created_date')
        batch_op.drop_column('confidence')
        batch_op.drop_column('visual_elements')
        batch_op.drop_column('campaign_name')
        batch_op.drop_column('target_audience')
        batch_op.drop_column('mail_piece_type')
        batch_op.drop_column('theme')
        batch_op.drop_column('color_scheme')

    with op.batch_alter_table('communication_focus', schema=None) as batch_op:
        batch_op.create_index('ix_communication_focus_primary_issue', ['primary_issue'], unique=False)
        batch_op.create_index('ix_communication_focus_document_id', ['document_id'], unique=False)
        batch_op.alter_column('primary_issue',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.drop_column('created_date')
        batch_op.drop_column('messaging_strategy')
        batch_op.drop_column('secondary_issues')

    with op.batch_alter_table('classifications', schema=None) as batch_op:
        batch_op.create_index('ix_classifications_document_id', ['document_id'], unique=False)
        batch_op.create_index('ix_classifications_category', ['category'], unique=False)
        batch_op.alter_column('category',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.drop_column('classification_date')
        batch_op.drop_column('confidence')

    op.drop_table('search_feedback')
    op.drop_table('dropbox_syncs')
    op.drop_table('clients')
    op.drop_table('batch_jobs')
    # ### end Alembic commands ###
