

import asyncio
import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sentient_agent_framework.implementation.default_hook import DefaultHook
from sentient_agent_framework.implementation.default_response_handler import DefaultResponseHandler
from sentient_agent_framework.implementation.default_session import DefaultSession
from sentient_agent_framework.interface.agent import AbstractAgent
from sentient_agent_framework.interface.events import DoneEvent
from sentient_agent_framework.interface.identity import Identity
from sentient_agent_framework.interface.request import Request

logger = logging.getLogger(__name__)


class BibleServerWithCORS:
    """
    Custom FastAPI server with CORS support for Bible Agent.
    Streams agent output to the client via Server-Sent Events.
    """

    def __init__(
            self,
            agent: AbstractAgent,
            allow_origins: list = None
        ):
        self._agent = agent

        # Create FastAPI app
        self._app = FastAPI(title="Bible Verse Agent API")
        
        # Add CORS middleware
        if allow_origins is None:
            # Allow all origins by default (use specific origins in production)
            allow_origins = ["*"]
        
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"]
        )
        
        logger.info(f"🌐 CORS enabled for origins: {allow_origins}")
        
        # Register endpoints
        self._app.post('/assist')(self.assist_endpoint)
        self._app.get('/health')(self.health_check)


    async def health_check(self):
        """Health check endpoint."""
        return {
            "status": "healthy",
            "agent": self._agent.name,
            "cors_enabled": True
        }


    def run(
            self, 
            host: str = "0.0.0.0",
            port: int = 8000
        ):
        """Start the FastAPI server"""
        logger.info(f"🚀 Starting server on {host}:{port}")
        uvicorn.run(
            self._app,
            host=host, 
            port=port,
            log_level="info"
        )


    async def __stream_agent_output(self, request: Request):
        """Yield agent output as SSE events."""

        try:
            # Get session from request
            session = DefaultSession(request.session)

            # Get identity using processor id from session
            identity = Identity(id=session.processor_id, name=self._agent.name)

            # Create response queue
            response_queue = asyncio.Queue()

            # Create hook
            hook = DefaultHook(response_queue)

            # Create response handler
            response_handler = DefaultResponseHandler(identity, hook)

            # Run the agent's assist function
            asyncio.create_task(
                self._agent.assist(session, request.query, response_handler)
            )
            
            # Stream the response handler events
            while True:
                event = await response_queue.get()
                
                # Format as proper SSE
                yield f"event: {event.event_name}\n"
                yield f"data: {event.model_dump_json()}\n\n"
                
                response_queue.task_done()
                
                if type(event) == DoneEvent:
                    break
                    
        except Exception as e:
            logger.error(f"❌ Stream error: {str(e)}", exc_info=True)
            
            # Send error event
            yield f"event: error\n"
            yield f'data: {{"error": "Internal server error: {str(e)}"}}\n\n'


    async def assist_endpoint(self, request: Request):
        """Endpoint that streams agent output to client as SSE events."""
        
        return StreamingResponse(
            self.__stream_agent_output(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }

        )
