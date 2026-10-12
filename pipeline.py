from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain


def run_resarch_pipeline(topic: str, on_step=None) -> dict:
    """
    Runs the 4-step research pipeline.

    on_step (optional): callback(stage_index, status) used by the Streamlit UI
    to show live progress. stage_index is 0-3, status is "working" or "done".
    Running this file from the terminal works exactly as before.
    """
    def notify(index, status):
        if on_step:
            on_step(index, status)

    state = {}

    # step 1 - search agent
    print("\n" + " =" * 50)
    print(" Step 1 - search agent is working ...")
    print("=" * 50)
    notify(0, "working")

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })

    state["search_results"] = search_result['messages'][-1].content
    print("\nSearch result ", state['search_results'])
    notify(0, "done")

    # step 2 - reader agent
    print("\n" + " =" * 50)
    print(" Step 2 - Reader agent is scraping top resources ...")
    print("=" * 50)
    notify(1, "working")

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{str(state['search_results'])[:800]}"
        )]
    })

    state["scraped_content"] = reader_result['messages'][-1].content
    print("\nscraped content\n", state["scraped_content"])
    notify(1, "done")

    # step 3 - writer chain
    print("\n" + " =" * 50)
    print(" Step 3 - writer is drafting the report ...")
    print("=" * 50)
    notify(2, "working")

    research_combined = (
        f"SEARCH RESULT :\n {state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\n Final Report \n", state["report"])
    notify(2, "done")

    # step 4 - critic
    print("\n" + " =" * 50)
    print(" Step 4 - Critic is reviewing the report ...")
    print("=" * 50)
    notify(3, "working")

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\n Critic Report\n", state['feedback'])
    notify(3, "done")

    return state


if __name__ == "__main__":
    topic = input("\nEnter research topic: ")
    run_resarch_pipeline(topic=topic)
