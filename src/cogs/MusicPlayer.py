import discord
from discord.ext import commands, bridge
import wavelink

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def connect_node(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host='192.168.0.120', port=2333, password='senha')

    @commands.Cog.listener()
    async def on_ready(self):
        await self.connect_node()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node {node.identifier} is ready.")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        ctx = player.ctx
        vc: player = ctx.voice_client

        if vc.loop == True: 
            return await vc.play(track)
        
        if vc.queue.is_empty:
            return await vc.disconnect()
        
        next_song = vc.queue.get()
        await vc.play(next_song)
        return await ctx.send(embed= discord.Embed(description= f"Now Playing {next_song.title}", colour= discord.Colour(0x7289da)))
    
    @bridge.bridge_command(name="play")
    async def play(self, ctx, query):

        async def embed(text, colour):
            await ctx.respond(embed= discord.Embed(description=text, colour= discord.Colour(colour)))

        channel = ctx.author.voice
        if channel:
            vc : wavelink.Player = ctx.voice_client or await ctx.author.voice.channel.connect(cls=wavelink.Player)

            try:
                playlist = await vc.node.get_playlist(wavelink.YouTubePlaylist, query)
                for track in playlist.tracks:
                    await vc.queue.put_wait(track)
            except:
                track = await wavelink.YouTubeTrack.search(query, return_first=True)
                await vc.queue.put_wait(track)

            if vc.is_playing():
                await embed(f"`{track.title}` Added to the queue!", 0x7289da)
            else:
                track = await vc.queue.get_wait()
                await embed(f"Now Playing: {track.title}", 0x7289da)
                await vc.play(track)
        else:
            await embed("You must be in the same voice channel as the bot", 0xe74c3c)

        vc.ctx = ctx
        setattr(vc, "loop", False)


    @bridge.bridge_command(name="skip")
    async def skip(self, ctx):
        async def embed(text, colour):
            await ctx.respond(embed= discord.Embed(description= text, colour= discord.Colour(colour)))

        vc: wavelink.Player = ctx.voice_client
        if ctx.author.voice.channel.id != vc.channel.id:
            await embed("You must be in the same voice channel as the bot.", 0xe74c3c)
        if vc.queue.is_empty:
            await embed(f"No more musics on queue", 0xe74c3c)
        else:
            await vc.stop()


    @bridge.bridge_command(name="leave")
    async def leave(self, ctx):
        vc = ctx.voice_client
        await vc.disconnect()
        return await ctx.respond(embed= discord.Embed(description="Leaving", colour=discord.Colour(0xe74c3c)))

    @bridge.bridge_command(name="clear")
    async def clear(self, ctx):
        async def embed(text, colour):
            return await ctx.respond(embed= discord.Embed(description= text, colour= discord.Colour(colour)))
        vc: wavelink.Player = ctx.voice_client
        if vc.queue.is_empty:
            await embed("Nothing to clean!", 0xe74c3c)
        else:
            try:
                await vc.queue.clear()
            except:
                await vc.stop()
                await embed("All going to trash!", 0xe74c3c)
    
    @bridge.bridge_command(name="volume")
    async def volume(self, ctx, volume):
        async def embed(text, colour):
            return await ctx.respond(embed= discord.Embed(description= text, colour= discord.Colour(colour)))
        try:
            volume = int(volume)
            if 0 < volume < 100:
                vc: wavelink.Player = ctx.voice_client
                if vc.is_connected():
                    await vc.set_volume(volume)
                    await embed(f"Volume set to {volume}", 0x7289da)
        except:
            await embed("Numbers Please!", 0xe74c3c)
    
    @bridge.bridge_command(name="stop")
    async def stop(self, ctx):
        async def embed(text, colour):
            return await ctx.respond(embed= discord.Embed(description= text, colour= discord.Colour(colour)))            
        vc: wavelink.Player = ctx.voice_client
        if vc.is_connected():
            if vc.is_paused():
                await vc.resume()
                await embed(f"Resuming!", 0x7289da)
            else:
                await vc.pause()
                await embed(f"Paused!", 0x7289da)
        else:
            await embed("You must be in the same voice channel as the bot.", 0xe74c3c)

    @bridge.bridge_command(name="loop")
    async def loop(self, ctx):
        async def embed(text, colour):
            return await ctx.respond(embed= discord.Embed(description= text, colour= discord.Colour(colour)))
        if not ctx.voice_client:
            await embed("Im not even in a voice channel", 0xe74c3c)
        elif not ctx.author.voice:
            await embed("Join a voice channel first!", 0xe74c3c)
        else:
            vc: wavelink.player = ctx.voice_client
        
        try:
            vc.loop ^= True
        except Exception:
            setattr(vc, "loop", False)
        
        if vc.loop == True:
            await embed("Loop is now Enabled!", 0x7289da)
        else:
            await embed("Loop is now Disabled", 0xe74c3c)

def setup(bot):
    bot.add_cog(MusicPlayer(bot))
