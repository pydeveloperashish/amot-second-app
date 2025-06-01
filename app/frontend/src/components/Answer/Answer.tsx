import { useMemo, useState } from "react";
import { Stack, IconButton } from "@fluentui/react";
import { useTranslation } from "react-i18next";
import DOMPurify from "dompurify";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";

import styles from "./Answer.module.css";
import { ChatAppResponse, getCitationFilePath, SpeechConfig, FeedbackType, sendFeedbackApi } from "../../api";
import { parseAnswerToHtml } from "./AnswerParser";
import { AnswerIcon } from "./AnswerIcon";
import { SpeechOutputBrowser } from "./SpeechOutputBrowser";
import { SpeechOutputAzure } from "./SpeechOutputAzure";
import { useLogin, getToken } from "../../authConfig";
import { useMsal } from "@azure/msal-react";

interface Props {
    answer: ChatAppResponse;
    index: number;
    speechConfig: SpeechConfig;
    isSelected?: boolean;
    isStreaming: boolean;
    onCitationClicked: (filePath: string) => void;
    onThoughtProcessClicked: () => void;
    onSupportingContentClicked: () => void;
    onFollowupQuestionClicked?: (question: string) => void;
    showFollowupQuestions?: boolean;
    showSpeechOutputBrowser?: boolean;
    showSpeechOutputAzure?: boolean;
}

export const Answer = ({
    answer,
    index,
    speechConfig,
    isSelected,
    isStreaming,
    onCitationClicked,
    onThoughtProcessClicked,
    onSupportingContentClicked,
    onFollowupQuestionClicked,
    showFollowupQuestions,
    showSpeechOutputAzure,
    showSpeechOutputBrowser
}: Props) => {
    const followupQuestions = answer.context?.followup_questions;
    const parsedAnswer = useMemo(() => parseAnswerToHtml(answer, isStreaming, onCitationClicked), [answer]);
    const { t } = useTranslation();
    const sanitizedAnswerHtml = DOMPurify.sanitize(parsedAnswer.answerHtml);
    const [copied, setCopied] = useState(false);
    const [feedback, setFeedback] = useState<FeedbackType | null>(null);
    const [feedbackLoading, setFeedbackLoading] = useState(false);
    
    const client = useLogin ? useMsal().instance : undefined;

    const handleCopy = () => {
        // Single replace to remove all HTML tags to remove the citations
        const textToCopy = sanitizedAnswerHtml.replace(/<a [^>]*><sup>\d+<\/sup><\/a>|<[^>]+>/g, "");

        navigator.clipboard
            .writeText(textToCopy)
            .then(() => {
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
            })
            .catch(err => console.error("Failed to copy text: ", err));
    };

    const handleFeedback = async (feedbackType: FeedbackType) => {
        if (feedbackLoading || !answer.session_state) return;
        
        setFeedbackLoading(true);
        try {
            const token = client ? await getToken(client) : undefined;
            
            // If user clicks the same feedback again, remove it
            if (feedback === feedbackType) {
                await sendFeedbackApi({
                    session_id: answer.session_state,
                    message_index: index,
                    feedback_type: "remove"
                }, token);
                setFeedback(null);
            } else {
                // Otherwise, set the new feedback
                await sendFeedbackApi({
                    session_id: answer.session_state,
                    message_index: index,
                    feedback_type: feedbackType
                }, token);
                setFeedback(feedbackType);
            }
        } catch (error) {
            console.error("Failed to send feedback:", error);
        } finally {
            setFeedbackLoading(false);
        }
    };

    return (
        <Stack className={`${styles.answerContainer} ${isSelected && styles.selected}`} verticalAlign="space-between">
            <Stack.Item>
                <Stack horizontal horizontalAlign="space-between">
                    <AnswerIcon />
                    <div>
                        <IconButton
                            style={{ color: "black" }}
                            iconProps={{ iconName: copied ? "CheckMark" : "Copy" }}
                            title={copied ? t("tooltips.copied") : t("tooltips.copy")}
                            ariaLabel={copied ? t("tooltips.copied") : t("tooltips.copy")}
                            onClick={handleCopy}
                        />
                        <IconButton
                            style={{ color: "black" }}
                            iconProps={{ iconName: "Lightbulb" }}
                            title={t("tooltips.showThoughtProcess")}
                            ariaLabel={t("tooltips.showThoughtProcess")}
                            onClick={() => onThoughtProcessClicked()}
                            disabled={!answer.context.thoughts?.length}
                        />
                        <IconButton
                            style={{ color: "black" }}
                            iconProps={{ iconName: "ClipboardList" }}
                            title={t("tooltips.showSupportingContent")}
                            ariaLabel={t("tooltips.showSupportingContent")}
                            onClick={() => onSupportingContentClicked()}
                            disabled={!answer.context.data_points}
                        />
                        {showSpeechOutputAzure && (
                            <SpeechOutputAzure answer={sanitizedAnswerHtml} index={index} speechConfig={speechConfig} isStreaming={isStreaming} />
                        )}
                        {showSpeechOutputBrowser && (
                            <SpeechOutputBrowser answer={sanitizedAnswerHtml} />
                        )}
                        
                        {/* Feedback buttons */}
                        <IconButton
                            className={`${styles.feedbackButton} ${feedback === "positive" ? styles.feedbackButtonActive : ""}`}
                            style={{ 
                                color: feedback === "positive" ? "#0078d4" : "black",
                                opacity: feedbackLoading ? 0.5 : 1
                            }}
                            iconProps={{ iconName: "Like" }}
                            title={t("tooltips.thumbsUp")}
                            ariaLabel={t("tooltips.thumbsUp")}
                            onClick={() => handleFeedback("positive")}
                            disabled={feedbackLoading || isStreaming}
                        />
                        <IconButton
                            className={`${styles.feedbackButton} ${feedback === "negative" ? styles.feedbackButtonActive : ""}`}
                            style={{ 
                                color: feedback === "negative" ? "#d13438" : "black",
                                opacity: feedbackLoading ? 0.5 : 1
                            }}
                            iconProps={{ iconName: "Dislike" }}
                            title={t("tooltips.thumbsDown")}
                            ariaLabel={t("tooltips.thumbsDown")}
                            onClick={() => handleFeedback("negative")}
                            disabled={feedbackLoading || isStreaming}
                        />
                    </div>
                </Stack>
            </Stack.Item>
            <Stack.Item>
                <div className={styles.answerText}>
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeRaw]}
                        children={sanitizedAnswerHtml}
                        className={styles.answerText}
                    />
                </div>
            </Stack.Item>
            {!!parsedAnswer.citations.length && (
                <Stack.Item>
                    <Stack horizontal wrap tokens={{ childrenGap: 5 }}>
                        <span className={styles.citationLearnMore}>{t("citationWithColon")}</span>
                        {parsedAnswer.citations.map((x, i) => {
                            const path = getCitationFilePath(x);
                            return (
                                <a key={i} className={styles.citation} title={x} onClick={() => onCitationClicked(path)}>
                                    {`${++i}. ${x}`}
                                </a>
                            );
                        })}
                    </Stack>
                </Stack.Item>
            )}

            {!!followupQuestions?.length && showFollowupQuestions && onFollowupQuestionClicked && (
                <Stack.Item>
                    <Stack horizontal wrap className={`${!!parsedAnswer.citations.length ? styles.followupQuestionsList : ""}`} tokens={{ childrenGap: 6 }}>
                        <span className={styles.followupQuestionLearnMore}>{t("followupQuestions")}</span>
                        {followupQuestions.map((x, i) => {
                            return (
                                <a key={i} className={styles.followupQuestion} title={x} onClick={() => onFollowupQuestionClicked(x)}>
                                    {`${x}`}
                                </a>
                            );
                        })}
                    </Stack>
                </Stack.Item>
            )}
        </Stack>
    );
};
