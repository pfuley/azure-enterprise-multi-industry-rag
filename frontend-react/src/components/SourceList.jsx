function SourceList({
    sources = [],
}) {

    if (!sources.length) {
        return null;
    }


    const uniqueSources = Array.from(
        new Map(
            sources.map(
                source => [
                    `${source.file_name}-${source.page_number}`,
                    source,
                ]
            )
        ).values()
    );


    return (
        <div className="sources">

            <div className="sources-title">
                Sources
            </div>


            <div className="source-grid">

                {uniqueSources.map(
                    source => (

                        <div
                            className="source-card"
                            key={
                                `${source.file_name}-${source.chunk_id}`
                            }
                        >

                            <div className="source-icon">
                                DOC
                            </div>


                            <div className="source-details">

                                <div className="source-name">
                                    {
                                        source.file_name
                                    }
                                </div>


                                <div className="source-meta">

                                    {
                                        source.page_number
                                            ? `Page ${source.page_number}`
                                            : "Knowledge base document"
                                    }

                                </div>

                            </div>

                        </div>

                    )
                )}

            </div>

        </div>
    );
}


export default SourceList;