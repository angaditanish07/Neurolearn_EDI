/**
 * Convert recorded audio (WebM/MP4) to WAV in the browser so the server
 * does not need ffmpeg for dyslexia reading analysis.
 */
window.NeuroLearnWav = {
    async blobToWav(blob, targetSampleRate) {
        const rate = targetSampleRate || 16000;
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        const decodeCtx = new AudioCtx();
        const arrayBuffer = await blob.arrayBuffer();
        let audioBuffer;
        try {
            audioBuffer = await decodeCtx.decodeAudioData(arrayBuffer);
        } finally {
            await decodeCtx.close();
        }

        const offline = new OfflineAudioContext(
            1,
            Math.max(1, Math.ceil(audioBuffer.duration * rate)),
            rate,
        );
        const source = offline.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(offline.destination);
        source.start(0);
        const rendered = await offline.startRendering();
        return new Blob([this._audioBufferToWav(rendered, rate)], { type: 'audio/wav' });
    },

    _audioBufferToWav(buffer, sampleRate) {
        const numChannels = 1;
        const samples = buffer.getChannelData(0);
        const length = samples.length;
        const dataLength = length * 2;
        const wavBuffer = new ArrayBuffer(44 + dataLength);
        const view = new DataView(wavBuffer);

        const writeString = (offset, str) => {
            for (let i = 0; i < str.length; i++) {
                view.setUint8(offset + i, str.charCodeAt(i));
            }
        };

        writeString(0, 'RIFF');
        view.setUint32(4, 36 + dataLength, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, numChannels, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * 2, true);
        view.setUint16(32, 2, true);
        view.setUint16(34, 16, true);
        writeString(36, 'data');
        view.setUint32(40, dataLength, true);

        let offset = 44;
        for (let i = 0; i < length; i++) {
            const s = Math.max(-1, Math.min(1, samples[i]));
            view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
            offset += 2;
        }

        return wavBuffer;
    },
};
