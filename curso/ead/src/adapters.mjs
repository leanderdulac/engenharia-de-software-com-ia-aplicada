/**
 * Adaptadores explicitamente desligados. Não fingir sucesso no UI.
 * SMTP, SSO, billing e streaming premium exigem conta/segredo externo.
 */
export const ADAPTERS = {
  smtp: { ligado: false, motivo: "EAD_SMTP_URL não implementado; recuperação de senha pendente." },
  sso: { ligado: false, motivo: "EAD_SSO_ISSUER não implementado; auth é senha local." },
  billing: { ligado: false, motivo: "Sem checkout. Matrícula local gratuita." },
  streaming: { ligado: false, motivo: "Vídeo/áudio servidos do disco do repo, sem CDN premium." },
};
