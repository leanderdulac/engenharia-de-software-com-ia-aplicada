/**
 * Adaptadores explicitamente desligados. Não fingir sucesso no UI.
 * SMTP, SSO, billing e streaming premium exigem conta/segredo externo.
 */
export const ADAPTERS = {
  smtp: {
    ligado: false,
    motivo: "Sem envio de e-mail. Redefinição é um token local de uso único (CLI ou instrutor), válido 30 min.",
  },
  sso: { ligado: false, motivo: "EAD_SSO_ISSUER não implementado; auth é senha local." },
  billing: { ligado: false, motivo: "Sem checkout. Matrícula local gratuita." },
  streaming: { ligado: false, motivo: "Vídeo/áudio servidos do disco do repo, sem CDN premium." },
};
