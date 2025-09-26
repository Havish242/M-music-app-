import streamlit as st
from audio_generator import generate_from_prompt, save_wav, remix_audio_from_file
from musicgen_integration import is_musicgen_available, generate_with_musicgen
import downloader
import tempfile
import os
from library import list_tracks, add_track, list_playlists, add_playlist, add_track_to_playlist, list_tracks_in_playlist


st.set_page_config(page_title="M Music App", layout="wide")

st.title("M Music App")

# Sidebar: library (simple Spotify-like list)
# Sidebar: library (simple Spotify-like list)
st.sidebar.title('Library')
tracks = list_tracks()
# Local song uploader (for adding your own songs, e.g., Telugu mp3s)
st.sidebar.markdown('### Add local song')
upload_file = st.sidebar.file_uploader('Upload MP3/WAV', type=['mp3', 'wav'])
song_title = st.sidebar.text_input('Title (optional)')
song_artist = st.sidebar.text_input('Artist (optional)')
if st.sidebar.button('Add uploaded song to library') and upload_file:
    lib_dir = os.path.join(os.path.dirname(__file__), 'library')
    os.makedirs(lib_dir, exist_ok=True)
    filename = upload_file.name
    dest = os.path.join(lib_dir, filename)
    with open(dest, 'wb') as f:
        f.write(upload_file.getbuffer())
    meta_title = song_title or os.path.splitext(filename)[0]
    prompt = f"Imported: {meta_title} by {song_artist}" if song_artist else f"Imported: {meta_title}"
    add_track(title=meta_title, file_path=dest, duration=0.0, prompt=prompt)
    st.sidebar.success(f'Added {meta_title} to library')
    # refresh tracks variable
    tracks = list_tracks()
    # update local tracks variable (Streamlit will re-render)
    st.sidebar.info('Library updated')

# Import from URL (YouTube, etc.)
st.sidebar.markdown('### Import from URL')
url_to_import = st.sidebar.text_input('Paste track URL')
confirm_rights = st.sidebar.checkbox('I confirm I have the rights to download/use this audio')
if st.sidebar.button('Import from URL') and url_to_import:
    if not confirm_rights:
        st.sidebar.error('You must confirm you have rights to use this content before importing')
    else:
        with st.spinner('Downloading audio...'):
            try:
                dl_path = downloader.download_audio_from_url(url_to_import)
                title = os.path.splitext(os.path.basename(dl_path))[0]
                add_track(title=title, file_path=dl_path, duration=0.0, prompt=f'Imported from {url_to_import}')
                st.sidebar.success(f'Imported {title} to library')
                tracks = list_tracks()
            except Exception as e:
                st.sidebar.error(f'Download failed: {e}')

st.sidebar.markdown('**Copyright note:** Only upload songs you own or have rights to use.')
# Playlists UI
st.sidebar.markdown('### Playlists')
pls = list_playlists()
new_pl_name = st.sidebar.text_input('New playlist name')
if st.sidebar.button('Create playlist') and new_pl_name:
    add_playlist(new_pl_name)

if pls:
    for pl in pls:
        if st.sidebar.button(f"View: {pl.get('name')}", key=f"viewpl_{pl['id']}"):
            st.session_state['view_playlist'] = pl['id']
else:
    st.sidebar.write('No playlists yet')

st.sidebar.markdown('---')
st.sidebar.write('Queue')
queue = st.session_state.get('queue', [])
cur_idx = st.session_state.get('queue_index', 0)
if queue:
    qtitle = queue[cur_idx].get('title', 'Unknown') if 0 <= cur_idx < len(queue) else 'Empty'
    st.sidebar.write(f'Now: **{qtitle}**')
    if st.sidebar.button('Prev'):
        st.session_state['queue_index'] = max(0, cur_idx - 1)
    if st.sidebar.button('Next'):
        st.session_state['queue_index'] = min(len(queue) - 1, cur_idx + 1)
else:
    st.sidebar.write('Queue is empty')
# Defensive: ensure tracks is a list (older library versions may return a dict)
if not isinstance(tracks, list):
    try:
        tracks = list(tracks.get('tracks', [])) if isinstance(tracks, dict) else list(tracks)
    except Exception:
        tracks = []

# selected playlist view handling
view_playlist_id = st.session_state.get('view_playlist')
if view_playlist_id:
    tracks = list_tracks_in_playlist(view_playlist_id)

if tracks:
    for t in tracks[:50]:
        st.sidebar.write(f"**{t.get('title')}** — {t.get('prompt', '')}")
        if st.sidebar.button('Play', key=f"play_{t['id']}"):
            # enqueue and set as current
            q = st.session_state.get('queue', [])
            q.append(t)
            st.session_state['queue'] = q
            st.session_state['queue_index'] = len(q) - 1
        if st.sidebar.button('Add to playlist', key=f"addpl_{t['id']}"):
            pls = list_playlists()
            if pls:
                add_track_to_playlist(pls[0]['id'], t['id'])
                st.sidebar.write('Added to first playlist')
            else:
                st.sidebar.write('No playlists available')
else:
    st.sidebar.write('Your library is empty. Generate or remix tracks and Save to Library.')

st.markdown(
    """
    Prototype that generates or remixes audio from a text prompt. This is not a full music model — replace `generate_from_prompt` with MusicGen for real results.
    """
)

# Mini player (main area)
st.markdown('## Player')
queue = st.session_state.get('queue', [])
q_index = st.session_state.get('queue_index', 0)
if queue and 0 <= q_index < len(queue):
    cur = queue[q_index]
    st.write(f"Now playing: **{cur.get('title')}**")
    try:
        st.audio(open(cur.get('file'), 'rb').read(), format='audio/wav')
    except Exception:
        st.write('Unable to play this track')
    if st.button('Remove from queue'):
        queue.pop(q_index)
        st.session_state['queue'] = queue
        st.session_state['queue_index'] = max(0, q_index - 1)
else:
    st.write('Player is empty — add a track from the sidebar')

model_choice = 'procedural'
if is_musicgen_available():
    model_choice = st.selectbox('Model', ['procedural', 'musicgen'])
else:
    st.info('MusicGen not available — using procedural generator')

mode = st.radio('Mode', ['Generate', 'Remix'])

if mode == 'Generate':
    with st.form('generate'):
        prompt = st.text_input('Enter prompt', value='Calm lofi with piano and rain sounds')
        style = st.selectbox('Style', ['lofi', 'edm', 'classical', 'default'])
        duration = st.slider('Duration (seconds)', min_value=5, max_value=60, value=15)
        mood = st.slider('Mood (calm -> energetic)', min_value=-1.0, max_value=1.0, value=0.0)
        submit = st.form_submit_button('Generate')

    if submit:
        with st.spinner('Generating audio...'):
            if model_choice == 'musicgen' and is_musicgen_available():
                try:
                    signal = generate_with_musicgen(prompt, duration=duration, device='cpu')
                except Exception as e:
                    st.error(f'MusicGen generation failed: {e}\nFalling back to procedural generator.')
                    signal = generate_from_prompt(prompt, duration=duration, style=style, mood=mood)
            else:
                signal = generate_from_prompt(prompt, duration=duration, style=style, mood=mood)
            tmpdir = tempfile.gettempdir()
            out_path = os.path.join(tmpdir, 'ai_music_output.wav')
            save_wav(signal, out_path)

        st.success('Done — play below')
        audio_file = open(out_path, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/wav')
        st.download_button('Download WAV', data=audio_bytes, file_name='ai_music_output.wav')
        if st.button('Save to Library'):
            # copy file to library folder
            lib_dir = os.path.join(os.path.dirname(__file__), 'library')
            os.makedirs(lib_dir, exist_ok=True)
            dest = os.path.join(lib_dir, f"gen_{int(os.path.getmtime(out_path))}.wav")
            with open(out_path, 'rb') as src, open(dest, 'wb') as dst:
                dst.write(src.read())
            add_track(title=prompt[:60] or 'Generated track', file_path=dest, duration=duration, prompt=prompt)
            st.success('Saved to library')

else:  
    st.subheader('Remix an uploaded MP3/WAV')
    uploaded = st.file_uploader('Upload audio file', type=['wav', 'mp3'])
    overlay_prompt = st.text_input('Optional motif prompt to overlay (short)')
    intensity = st.slider('Remix intensity', min_value=0.0, max_value=1.0, value=0.5)
    mood = st.slider('Mood (calm -> energetic)', min_value=-1.0, max_value=1.0, value=0.0)
    if st.button('Remix'):
        if not uploaded:
            st.warning('Please upload a file first')
        else:
            tmpdir = tempfile.gettempdir()
            in_path = os.path.join(tmpdir, uploaded.name)
            with open(in_path, 'wb') as f:
                f.write(uploaded.getbuffer())
            with st.spinner('Remixing...'):
                signal = remix_audio_from_file(in_path, intensity=intensity, overlay_prompt=overlay_prompt or None, mood=mood)
                out_path = os.path.join(tmpdir, 'ai_music_remix.wav')
                save_wav(signal, out_path)

            st.success('Remix done — play below')
            audio_file = open(out_path, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/wav')
            st.download_button('Download Remix WAV', data=audio_bytes, file_name='ai_music_remix.wav')
            if st.button('Save Remix to Library'):
                lib_dir = os.path.join(os.path.dirname(__file__), 'library')
                os.makedirs(lib_dir, exist_ok=True)
                dest = os.path.join(lib_dir, f"remix_{int(os.path.getmtime(out_path))}.wav")
                with open(out_path, 'rb') as src, open(dest, 'wb') as dst:
                    dst.write(src.read())
                add_track(title=(overlay_prompt or 'Remix')[:60], file_path=dest, duration=0.0, prompt=overlay_prompt)
                st.success('Saved remix to library')

st.markdown('---')
st.header('Next steps / integration')
st.markdown(
    """
    - To integrate a real model, install the model package (e.g. Meta's MusicGen / audiocraft) and replace `generate_from_prompt` to call the model.
    - Add a lyrics generator using GPT-4 via OpenAI API and optional TTS/singing model.
    - Store generated files to AWS S3 / Firebase for persistence.
    """
)
