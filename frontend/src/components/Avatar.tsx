import React from "react";
import { motion } from "framer-motion";

interface AvatarProps {
  avatarUrl: string;
  isLoading: boolean;
}

const Avatar: React.FC<AvatarProps> = ({ avatarUrl, isLoading }) => {
  return (
    <div className="flex justify-center items-center">
      {isLoading ? (
        <div className="animate-spin h-16 w-16 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      ) : (
        <motion.img
          src={avatarUrl || "/avatar-placeholder.png"}
          alt="Avatar"
          className="w-32 h-32 rounded-full"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        />
      )}
    </div>
  );
};

export { Avatar as default };